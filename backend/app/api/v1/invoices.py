from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.invoice import Invoice, InvoiceStatus
from app.models.user import User, UserRole
from app.schemas.invoice import InvoiceCreate, InvoiceStatusUpdate, InvoiceResponse
from app.models.investment import Investment

router = APIRouter()

#1. Submit an invoice(Borrower)
@router.post("/", response_model=InvoiceResponse,
status_code=status.HTTP_201_CREATED)
def submit_invoice(invoice_in: InvoiceCreate, db: Session = Depends(get_db)):
    # check if borrower exists and is actually a borrower
    borrower = db.query(User).filter(User.id == invoice_in.borrower_id).first()
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")
    if borrower.role != UserRole.BORROWER:
        raise HTTPException(status_code=400, detail="Only registered borrowers can submit invoices")
    
    new_invoice = Invoice(
        borrower_id=invoice_in.borrower_id,
        amount=invoice_in.amount,
        yield_rate=invoice_in.yield_rate,
        client_name=invoice_in.client_name,
        due_date=invoice_in.due_date,
        status=InvoiceStatus.PENDING #always starts as pending admin review
    )
    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)
    return new_invoice

#2. Marketplace: view all approved Invoices available for lenders to fund
@router.get("/marketplace",
            response_model=list[InvoiceResponse])
def get_marketplace_invoices(db: Session = Depends(get_db)):
    invoices = db.query(Invoice).filter(Invoice.status == InvoiceStatus.APPROVED).all()
    return invoices
               
#3. admin update invoice status (e.g. approve or reject after vetting
@router.patch("/{invoice_id}/status", response_model=InvoiceResponse)
def update_invoice_status(invoice_id: int, status_update:
    InvoiceStatusUpdate, db: Session = Depends(get_db)):
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
            
        invoice.status = status_update.status
        db.commit()
        db.refresh(invoice)
        return invoice



#4. View detailed status of an invoice (Funding progress, remaining amount, investors)
@router.get("/{invoice_id}/details")
def get_invoice_details(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    investments = db.query(Investment).filter(Investment.invoice_id == invoice.id).all()
    total_funded = sum([inv.amount for inv in investments])
    remaining_amount = max(0.0, invoice.amount - total_funded)
    
    return{
        "invoice_id": invoice.id,
        "client_name": invoice.client_name,
        "amount": invoice.amount,
        "yield_rate": invoice.yield_rate,
        "status": invoice.status.value,
        "due_date": invoice.due_date,
        "total_funded": total_funded,
        "remainning_amount": remaining_amount,
        "funding_percentage": round((total_funded / invoice.amount)*100, 2)if invoice.amount > 0 else 0,
        "investment_count": len (investments)
        
    }

#5. settle/ reay invoice (calculates lender payouts + provision fund deduction)
@router.post("/{invoice_id}/repay")
def repay_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if invoice.status != InvoiceStatus.FUNDED:
        raise HTTPException(
            status_code=400,
            detail=f"Only fully FUNDED invoicces can be settled. Current status: {invoice.status.value}"
         )
    #all lenders who funded this invoice
    investments = db.query(Investment).filter(Investment.invoice_id == invoice.id).all()
    
    #total interest generated( eg 100,00*0.15 = 15,000 KES)
    total_interest = invoice.amount * invoice.yield_rate
    gross_repayment = invoice.amount + total_interest
    
    #platfom and provision fee(2% total of gross repayment)
    #1% to platform revenue, 1% goes to the emergency provision fund
    provision_fund_fee = gross_repayment * 0.01
    platform_revenue_fee = gross_repayment * 0.01
    net_interest_for_lenders = total_interest - (provision_fund_fee + platform_revenue_fee)
    
    #proportional payout calculation for each lender
    payouts = []
    for inv in investments:
        #proporion of invoice this lender provided
        share_ratio = inv.amount / invoice.amount
        lender_profit = net_interest_for_lenders * share_ratio
        total_payout = inv.amount + lender_profit
        
        payouts.append({
            "lender_id": inv.lender_id,
            "principal_returned": inv.amount,
            "net_profit":round(lender_profit, 2),
            "total_payout": round(total_payout,2)
        })
        
    #close the invoice
    invoice.status = InvoiceStatus.REPAID
    db.commit()
    
    return{
        "message": "Invoice successfull settled and marked as REPAID",
        "invoice_id": invoice.id,
        "gross_repaid": gross_repayment,
        "platform_fee": round(platform_revenue_fee, 2),
        "payouts": payouts
    }