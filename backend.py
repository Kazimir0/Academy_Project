from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
from database import SessionLocal, engine, Base, Product  # Import Product from database
from schemas import ProductCreate

# Initialize FastAPI app
app = FastAPI()
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Add product endpoint
@app.post("/products/")
async def add_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        # Asigură-te că directorul pentru imagini există
        os.makedirs("./static/images", exist_ok=True)

        # Citește conținutul imaginii
        image_content = await image.read()
        image_filename = image.filename  # Numele fișierului de imagine

        # Salvează imaginea pe disc
        with open(f"./static/images/{image_filename}", "wb") as f:
            f.write(image_content)

        # Adaugă produsul în baza de date
        new_product = Product(name=name, description=description, price=price, image_url=f"/images/{image_filename}")
        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        return JSONResponse(content={"message": "Product added successfully!", "product": new_product.id}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
