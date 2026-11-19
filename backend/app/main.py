from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.api import api_router
from fastapi.middleware.cors import CORSMiddleware

#--NEW DATABASE IMPORTS--
from app.core.database import engine, Base
from app.models import user, invoice, investment, transaction

# Tell SQLAlchemy to create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="254 Finance API",
              version="1.0.0",
              openapi_url=f"{settings.API_V1_STR}/openapi.json")

app.include_router(api_router, prefix=settings.API_V1_STR)
#include all modular routes under the /api/v1 prefix
@app.get("/")
def root():
    return {
        
        "message": "Welcome to 254 Finance ",
       
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)