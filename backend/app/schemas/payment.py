from pydantic import BaseModel, Field

class STKPushRequest(BaseModel):
    phone_number: str = Field(..., example="254712345678", description="Kenyan mobile numbr")
    amount: float = Field(..., gt=0, example=1000.0, description="Amount in KES")
    invoice_id: int = Field(..., description="The invoice ID being funded")
    lender_id: int = Field(..., description="The lender uder ID")
    
class STKPushResponse(BaseModel):
    MerchantRequestID: str
    CheckoutRequestID: str
    ResponseCode:str
    RespoonseDescription: str
    CustomerMessage: str