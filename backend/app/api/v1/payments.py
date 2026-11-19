from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import List

from app.core.database import get_db
from app.services.mpesa import mpesa_service
from app.schemas.payment import STKPushRequest
from app.models.transaction import Transaction, TransactionStatus, TransactionType
from app.models.investment import Investment
from app.models.invoice import Invoice, InvoiceStatus

router = APIRouter()

@router.post("/stk-push")
async def trigger_stk_push(payload: STKPushRequest, db: Session = Depends(get_db)):
    """
    Trigger STK Push to prompt a lender's phone for payment PIN
    and create an initial pending Transaction record.
    """
    try:
        response = await mpesa_service.initiate_stk_push(
            phone_number=payload.phone_number,
            amount=payload.amount,
            account_reference=f"INV-{payload.invoice_id}",
            transaction_desc=f"Fund Invoice {payload.invoice_id}"
        )

        merchant_request_id = response.get("MerchantRequestID")
        checkout_request_id = response.get("CheckoutRequestID")

        # Save pending transaction to track this specific payment
        db_transaction = Transaction(
            user_id=payload.lender_id,
            invoice_id=payload.invoice_id,
            amount=payload.amount,
            phone_number=payload.phone_number,
            merchant_request_id=merchant_request_id,
            checkout_request_id=checkout_request_id,
            transaction_type=TransactionType.DEPOSIT,
            status=TransactionStatus.PENDING,
            result_code=int(response.get("ResponseCode", 0)) if response.get("ResponseCode") else None,
            result_desc=response.get("ResponseDescription")
        )
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)

        return {
            "daraja_response": response,
            "transaction_id": db_transaction.id,
            "status": "pending_user_pin"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mpesa/callback")
async def mpesa_callback(request: Request, db: Session = Depends(get_db)):
    """
    Webhook callback hit by Safaricom once user enters PIN.
    Parses payment status, updates transaction record, and automatically creates the Investment.
    """
    callback_data = await request.json()
    print("M-PESA CALLBACK RECEIVED:", callback_data)

    stk_callback = callback_data.get("Body", {}).get("stkCallback", {})
    checkout_request_id = stk_callback.get("CheckoutRequestID")
    merchant_request_id = stk_callback.get("MerchantRequestID")
    result_code = stk_callback.get("ResultCode")
    result_desc = stk_callback.get("ResultDesc")

    # Find the matching pending transaction
    tx = db.query(Transaction).filter(
        Transaction.checkout_request_id == checkout_request_id
    ).first()

    if not tx:
        # Fallback query with MerchantRequestID if checkout ID isn't found
        tx = db.query(Transaction).filter(
            Transaction.merchant_request_id == merchant_request_id
        ).first()

    if tx:
        tx.result_code = result_code
        tx.result_desc = result_desc

        if result_code == 0:
            # ResultCode 0 = Payment successful!
            tx.status = TransactionStatus.COMPLETED

            # Extract receipt number and amount from metadata
            metadata_items = stk_callback.get("CallbackMetadata", {}).get("Item", [])
            for item in metadata_items:
                name = item.get("Name")
                val = item.get("Value")
                if name == "MpesaReceiptNumber":
                    tx.mpesa_receipt_number = str(val)
                elif name == "Amount" and val:
                    tx.amount = float(val)

            # --- AUTOMATIC FUNDING LOGIC ---
            if tx.invoice_id:
                invoice = db.query(Invoice).filter(Invoice.id == tx.invoice_id).first()
                if invoice:
                    # Create the new confirmed Investment record
                    new_investment = Investment(
                        lender_id=tx.user_id,
                        invoice_id=tx.invoice_id,
                        amount=tx.amount
                    )
                    db.add(new_investment)

                    # Check total funded so far to see if invoice is 100% complete
                    current_funded = (
                        db.query(func.coalesce(func.sum(Investment.amount), 0.0))
                        .filter(Investment.invoice_id == invoice.id)
                        .scalar()
                    )

                    if (current_funded + tx.amount) >= invoice.amount:
                        invoice.status = InvoiceStatus.FUNDED

        else:
            # User canceled, wrong PIN, or insufficient funds
            tx.status = TransactionStatus.FAILED

        db.commit()

    return {"ResultCode": 0, "ResultDesc": "Accepted"}


@router.get("/transactions/{user_id}")
def get_user_transactions(user_id: int, db: Session = Depends(get_db)):
    """
    List all payment transactions (deposits, disbursements) for a user.
    """
    transactions = db.query(Transaction).filter(Transaction.user_id == user_id).order_by(Transaction.created_at.desc()).all()
    return transactions
