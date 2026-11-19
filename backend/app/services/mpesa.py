import base64
from datetime import datetime
import httpx
from app.core.config import settings

class MpesaService:
    def __init__(self):
        if settings.MPESA_ENVIRONMENT == "sandbox":
            self.base_url = "https://sandbox.safaricom.co.ke"
        else:
            self.base_url = "https://api.safaricom.co.ke"
            
    async def get_access_token(self) -> str:
        """Fetch OAuth2 Bearer token from Safaricom Daraja."""
        auth_url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        
        # Combine consumer key and secret with basic auth
        keys = f"{settings.MPESA_CONSUMER_KEY}:{settings.MPESA_CONSUMER_SECRET}"
        encoded_auth = base64.b64encode(keys.encode()).decode("utf-8")
        
        headers = {
            "Authorization": f"Basic {encoded_auth}"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(auth_url, headers=headers)
            if response.status_code != 200:
                raise Exception(f"Failed to get M-Pesa access token: {response.text}")
            return response.json().get("access_token")
        
    def generate_password(self, timestamp: str) -> str:
        """Generate Lipa Na Mpesa Online base64 password."""
        raw_password = f"{settings.MPESA_BUSINESS_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
        return base64.b64encode(raw_password.encode()).decode("utf-8")
    
    async def initiate_stk_push(self, phone_number: str, amount: float, account_reference: str, transaction_desc: str):
        """
        Trigger STK Push to user's phone.
        phone_number must be in format 2547xxxxxxxx or 2541xxxxxxxx.
        """
        # Format Kenyan phone number to 254...
        formatted_phone = phone_number.strip().replace("+", "")
        if formatted_phone.startswith("0"):
            formatted_phone = "254" + formatted_phone[1:]
            
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = self.generate_password(timestamp)
        token = await self.get_access_token()
        
        stk_url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        } 
        
        payload = {
            "BusinessShortCode": settings.MPESA_BUSINESS_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": formatted_phone,
            "PartyB": settings.MPESA_BUSINESS_SHORTCODE,
            "PhoneNumber": formatted_phone,
            "CallBackURL": settings.MPESA_CALLBACK_URL,
            "AccountReference": account_reference,
            "TransactionDesc": transaction_desc
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(stk_url, json=payload, headers=headers)
            return response.json()
        
mpesa_service = MpesaService()