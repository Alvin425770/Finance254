from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Investment(Base):
    __tablename__= "investments"
    id = Column(Integer, primary_key=True, index=True)
    
    #who is funding
    lender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    #which invoice is being funded
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    
    #How muchthey are putting
    amount = Column(Float, nullable=False)
    
    #timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    #Relationships for easy lookup
    lender = relationship("User")
    Invoice = relationship("Invoice")