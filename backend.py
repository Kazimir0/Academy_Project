from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
from database import SessionLocal, engine, Base, Product, User
from passlib.context import CryptContext

# Initialize FastAPI app
app = FastAPI()
Base.metadata.create_all(bind=engine)

# Hashing for password crypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint for user authentication
@app.post("/login/")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not pwd_context.verify(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Accessing user_id after successful login
    user_id = user.user_id  # This is where you use user_id instead of id
    return {"message": "Login successful!", "user_id": user_id}  # Returning user_id in the response

# Endpoint for adding product
@app.post("/products/")
async def add_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        os.makedirs("./static/images", exist_ok=True)
        image_content = await image.read()
        image_filename = image.filename
        with open(f"./static/images/{image_filename}", "wb") as f:
            f.write(image_content)

        new_product = Product(name=name, description=description, price=price, image_url=f"/images/{image_filename}")
        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        return JSONResponse(content={"message": "Product added successfully!", "product": new_product.id}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
