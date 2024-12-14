from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Load environment variables from the .env file
load_dotenv()

# 2. Get the database URL from the environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Check if the DATABASE_URL exists
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set!")

# 3. Database configuration
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 4. Define the Product model
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    description = Column(String)
    price = Column(Float)
    image_url = Column(String)

# 5. Function to initialize the database
def init_db():
    Base.metadata.create_all(bind=engine)
