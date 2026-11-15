from pydantic import BaseModel, Field
from datetime import datetime
from app.models.invoice import InvoiceStatus

#1. what an sme sends when submitting an invoice
class InvoiceCreate(BaseModel):
    borrower_id:int
    amount:float = Field(..., gt=0, description="Invoice amount in KES, e.g., 50000.0")
    yield_rate:float = Field(..., gt=0, le=1, description="Annualized or fixed return rate, e.g., 0.12 for 12%")
    client_name:str = Field(..., example="Naivas Supermarkets ltd")
    due_date: datetime
    
#2. what admin sends to approve or reject an incoice
class InvoiceStatusUpdate(BaseModel):
    status: InvoiceStatus
    
#3. What API returns when viewing invoices
class InvoiceResponse(BaseModel):
    id:int
    borrower_id:int
    amount:float
    yield_rate:float
    client_name:str
    due_date: datetime
    status: InvoiceStatus
    created_at: datetime
    
    class Config:
        from_attributes = True