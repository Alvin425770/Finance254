from sqlalchemy import Column, Integer, String, Float, Enum, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base

#the lifecycle of an invoice on the platform
class InvoiceStatus(str, enum.Enum):
    PENDING = "pending" #Uploaded by SME, waiting for admin vetting
    APPROVED = "approved" #Approved by admin, now visible to lenders
    FUNDED = "funded" #Fully funded by lenders, waiting for SME to pay back
    REPAID = "repaid" #SME has paid back the loan, invoice is closed
    DEFAULTED = "defaulted" #SME has failed to pay back the loan, (Provision fund kicks in)
    
class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    
    #link the invoice to the borrower who uploaded it
    borrower_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    #financial details
    amount = Column(Float, nullable=False) #eg 100.00kes
    yield_rate = Column(Float, nullable=False) #eg 0.15 for 15% interest
    
    #invoice metadata
    client_name = Column(String, nullable=False) #the SME who owes the money
    due_date = Column(DateTime, nullable=False) #when the SME is expected to pay
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.PENDING, nullable=False)
    
    #Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    #alllow us easily fetch the user details when looking at an invoice
    borrower = relationship("User")