import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Carpet, Order, Review

app = FastAPI(title="Persian Carpets API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Persian Carpets Backend Running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response

# Utilities
class CatalogQuery(BaseModel):
    region: Optional[str] = None
    style: Optional[str] = None
    max_price: Optional[float] = None
    featured_only: bool = False

@app.post("/api/carpets")
def create_carpet(carpet: Carpet):
    try:
        carpet_id = create_document("carpet", carpet)
        return {"id": carpet_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/carpets/query")
def query_carpets(q: CatalogQuery):
    try:
        filt = {}
        if q.region:
            filt["region"] = q.region
        if q.style:
            filt["style"] = q.style
        if q.max_price is not None:
            filt["price_usd"] = {"$lte": q.max_price}
        if q.featured_only:
            filt["is_featured"] = True
        carpets = get_documents("carpet", filt, limit=50)
        for c in carpets:
            c["_id"] = str(c.get("_id"))
        return carpets
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/carpets/{carpet_id}")
def get_carpet(carpet_id: str):
    try:
        doc = db["carpet"].find_one({"_id": ObjectId(carpet_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Carpet not found")
        doc["_id"] = str(doc["_id"])
        return doc
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/orders")
def create_order(order: Order):
    try:
        order_id = create_document("order", order)
        return {"id": order_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reviews")
def create_review(review: Review):
    try:
        review_id = create_document("review", review)
        return {"id": review_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Sample seeding endpoint (optional for demo)
@app.post("/api/seed")
def seed_demo_data():
    try:
        if db["carpet"].count_documents({}) > 0:
            return {"status": "ok", "message": "Catalog already seeded"}
        samples: List[Carpet] = [
            Carpet(
                title="Isfahan Silk Medallion",
                description="Fine silk-on-silk with central medallion and arabesque borders.",
                region="Isfahan",
                style="medallion",
                size_cm="200 x 300",
                materials=["silk"],
                knot_density_kpsi=650,
                age_years=15,
                price_usd=48000,
                images=[
                    "https://images.unsplash.com/photo-1545239351-1141bd82e8a6?q=80&w=1600&auto=format&fit=crop",
                ],
                colors=["crimson", "ivory", "navy"],
                rarity_score=0.92,
                is_featured=True,
                in_stock=True,
            ),
            Carpet(
                title="Tabriz Garden of Paradise",
                description="Wool and silk blend with garden panels and cypress trees.",
                region="Tabriz",
                style="garden",
                size_cm="240 x 340",
                materials=["wool", "silk"],
                knot_density_kpsi=400,
                age_years=25,
                price_usd=28000,
                images=[
                    "https://images.unsplash.com/photo-1618220179428-22790b461013?q=80&w=1600&auto=format&fit=crop",
                ],
                colors=["emerald", "gold", "brick"],
                rarity_score=0.8,
                is_featured=True,
                in_stock=True,
            ),
            Carpet(
                title="Kashan Royal Court",
                description="Antique wool masterpiece with courtly motifs and deep palette.",
                region="Kashan",
                style="pictorial",
                size_cm="180 x 270",
                materials=["wool"],
                knot_density_kpsi=300,
                age_years=70,
                price_usd=36000,
                images=[
                    "https://images.unsplash.com/photo-1545239350-48bf079fb38e?q=80&w=1600&auto=format&fit=crop",
                ],
                colors=["ruby", "indigo", "beige"],
                rarity_score=0.86,
                is_featured=False,
                in_stock=True,
            ),
        ]
        for s in samples:
            create_document("carpet", s)
        return {"status": "ok", "message": "Seeded sample carpets"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
