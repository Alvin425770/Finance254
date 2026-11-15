from pydantic import BaseModel
from app.models.user import UserRole

#1. What the frontend sends to us when registering
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    phone_number: str
    role: UserRole
    
#2. What we return to the frontend(no passwords)
class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone_number: str
    role: UserRole
    is_active: bool
    is_verified: bool
    
    class Config:
        from_attributes = True #this tells pydantic to read from our SQLAlchemy database