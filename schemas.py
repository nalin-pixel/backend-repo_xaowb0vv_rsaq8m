"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Carpet(BaseModel):
    """
    Persian carpets catalog
    Collection name: "carpet"
    """
    title: str = Field(..., description="Carpet name")
    description: Optional[str] = Field(None, description="Detailed description and craftsmanship notes")
    region: str = Field(..., description="Origin region, e.g., Tabriz, Kashan, Isfahan")
    style: str = Field(..., description="Design style, e.g., medallion, garden, pictorial")
    size_cm: str = Field(..., description="Size in cm, e.g., 200 x 300")
    materials: List[str] = Field(default_factory=list, description="Materials used, e.g., wool, silk")
    knot_density_kpsi: Optional[int] = Field(None, description="Knots per square inch")
    age_years: Optional[int] = Field(None, description="Estimated age in years")
    price_usd: float = Field(..., ge=0, description="Price in USD")
    images: List[str] = Field(default_factory=list, description="Image URLs")
    colors: List[str] = Field(default_factory=list, description="Dominant colors")
    rarity_score: Optional[float] = Field(None, ge=0, le=1, description="0-1 index for rarity")
    is_featured: bool = Field(False, description="Mark as featured for the gallery hero")
    in_stock: bool = Field(True, description="Availability")

class Review(BaseModel):
    """
    Customer reviews for carpets
    Collection name: "review"
    """
    carpet_id: str = Field(..., description="Referenced carpet _id as string")
    name: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class OrderItem(BaseModel):
    carpet_id: str
    quantity: int = Field(1, ge=1)
    price_usd: float

class Order(BaseModel):
    """
    Orders
    Collection name: "order"
    """
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = None
    shipping_address: str
    items: List[OrderItem]
    subtotal_usd: float
    upsell_ids: List[str] = Field(default_factory=list, description="IDs of upsold items if any")
    notes: Optional[str] = None

# Legacy example kept for reference
class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
