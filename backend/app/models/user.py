from sqlalchemy import Column, Integer, String, Boolean, Enum, DateTime
from sqlalchemy.sql import func
import enum
from app.core.database import Base

#Define roles in the system
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    LENDER = "lender"  #people funding loans
    BORROWER = "borrower" #Someone taking a loan
    
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    #identity and contact
    full_name = Column(String, nullable=False)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.LENDER, nullable=False)
    
    #RISK AND KYC
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)#set to true only after Id and Crb are checks pass
    
    #audit timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())