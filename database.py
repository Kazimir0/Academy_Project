from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Database Configuration
DATABASE_URL = "mssql+pyodbc://sa:Magazin123@localhost/products?driver=ODBC+Driver+17+for+SQL+Server"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. Define the Product Model
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)  
    description = Column(String)       
    price = Column(Float)
    image_url = Column(String)  # Path to the product image file


def init_db():
    Base.metadata.create_all(bind=engine)
