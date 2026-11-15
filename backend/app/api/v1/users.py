from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.core.database import get_db
from app.models.user import User
from app.schemas.users import UserCreate, UserResponse

router = APIRouter()

#setup password hashing system
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register", response_model=UserResponse)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    
    #1. check if email already exists
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    existing_phone = db.query(User).filter(User.phone_number == user_in.phone_number).first()
    if existing_phone:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    #2. hash the password
    hashed_pw = pwd_context.hash(user_in.password)
    
    #3. create the database row
    new_user = User(
        email=user_in.email,
        hashed_password=hashed_pw,
        full_name=user_in.full_name,
        phone_number=user_in.phone_number,
        role=user_in.role
    )
    
    #4. Save to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user
    

