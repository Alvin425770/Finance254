from pydantic import BaseModel, Field
from datetime import datetime

#What a lender sends when funding an invoice
class InvestmentCreate(BaseModel):
    lender_id: int
    invoice_id: int
    amount: float = Field(..., gt=0, descriptions= "Amount to invest in KES, e.g., 5000.00")
    
    #what the api returns after an investment is made
class InvestmentResponse(BaseModel):
    id: int
    lender_id: int
    invoice_id: int
    amount: float 
    created_at: datetime
        
    class Config:
        from_attributes = True
        