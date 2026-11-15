from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

#create the sqlalchemy engine(connect_args is needed specifically for SQLite)
engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)

#his creates a database session whenever the API needs to talk to the DB
Sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#all our future database models (users, invoices)will inherit from this base
Base = declarative_base()

#We will use this function to inject the database into our API routes
def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()