from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import List

from app.core.database import get_db
from app.models.investment import Investment
from app.models.invoice import Invoice, InvoiceStatus
from app.models. user import User, UserRole
from app.schemas.investment import InvestmentCreate, InvestmentResponse

router = APIRouter()

@router.post("/", response_model=InvestmentResponse, status_code=status.HTTP_201_CREATED)
def fund_invoice(investment_in: InvestmentCreate, db: Session = Depends(get_db)):
     #1. Validate that user exists and is a lender
    lender = db.query(User).filter(User.id == investment_in.lender_id).first()
    if not lender:
        raise HTTPException(status_code=404, detail="Lender not found")
    if lender.role != UserRole.LENDER:
        raise HTTPException(status_code=400, detail="Only registered leners can invest in invoices")
        
    #2. Validate that the invoice exists and is APPROVED(OPEN FO FUNDING)
    invoice = db.query(Invoice).filter(Invoice.id == investment_in.invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if invoice.status != InvoiceStatus.APPROVED:
        raise HTTPException(
        status_code=400,
        detail=f"Invoice cannot be funded. Current status: {invoice.status.value}"
    )  
    
    #3. Calculate how much has already been funded onthis invoice
    current_funded = (
        db.query(func.coalesce(func.sum(Investment.amount),0.0))
        .filter(Investment.invoice_id == invoice.id)
        .scalar()
    )          
    
    remaining_needed = invoice.amount - current_funded
    
    #4. check if this investment exceeds to invoice requirement
    if investment_in.amount > remaining_needed:
        raise HTTPException(
            status_code=400,
            detail=f"Investment exceeds remaining target. Only KES {remaining_needed:,.2f}is needed."
        )

    #5. record the investment
    new_investment = Investment(
        lender_id=investment_in.lender_id,
        invoice_id=investment_in.invoice_id,
        amount=investment_in.amount
    )
    db.add(new_investment)
    
    #6. if the investment completes the target, automatically set status to FUNDED
    if (current_funded + investment_in.amount) >= invoice.amount:
        invoice.status = InvoiceStatus.FUNDED
        
        db.commit()
        db.refresh(new_investment)
        return new_investment
    
    #list all investments made by a specific lender
    @router.get("/lender/{lender_id}", response_model=List[InvestmentResponse])
    def get_lender_investments(lender_id: int, db:Session = Depends(get_db)):
        investments = db.query(Investment).filter(Investment.lender_id == lender_id).all()
        return investments


