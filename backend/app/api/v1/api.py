from fastapi import APIRouter
from app.api.v1 import users, invoices, investments, payments
#we will import invoices, mpesa,etc here later

api_router = APIRouter()

#attach the users module
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["Invoices"])
api_router.include_router(investments.router, prefix="/investments", tags=["Investments"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments (M-Pesa)"])
