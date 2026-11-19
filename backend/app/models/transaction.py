from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base

class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class TransactionType(str, enum.Enum):
    DEPOSIT = "deposit"       # Lender depositing / funding via STK push
    DISBURSEMENT = "disbursement" # Platform sending loan to SME
    REPAYMENT = "repayment"   # SME paying back invoice
    WITHDRAWAL = "withdrawal" # Lender withdrawing profits

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)

    amount = Column(Float, nullable=False)
    phone_number = Column(String, nullable=True)

    # Safaricom Daraja identifiers
    merchant_request_id = Column(String, nullable=True, index=True)
    checkout_request_id = Column(String, nullable=True, index=True)
    mpesa_receipt_number = Column(String, nullable=True, unique=True, index=True)

    transaction_type = Column(Enum(TransactionType), default=TransactionType.DEPOSIT, nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)

    result_code = Column(Integer, nullable=True)
    result_desc = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User")
    invoice = relationship("Invoice")
