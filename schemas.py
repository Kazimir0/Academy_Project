from pydantic import BaseModel

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    image_url: str  # Field for image URLs; adjust if handling uploads differently
