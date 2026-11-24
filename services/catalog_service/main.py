from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import List, Optional
import datetime

app = FastAPI(
    title="Catalog Microservice",
    description="Product catalog and inventory microservice",
    version="1.0.0"
)

class Product(BaseModel):
    id: int
    name: str
    category: str
    price: float
    stock: int
    description: Optional[str] = None

class ProductCreate(BaseModel):
    name: str
    category: str
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    description: Optional[str] = None

CATALOG_DB = {
    1: Product(id=1, name="Cloud Server Instance Small", category="Compute", price=15.0, stock=50, description="1 vCPU, 2GB RAM"),
    2: Product(id=2, name="Cloud Server Instance Large", category="Compute", price=60.0, stock=20, description="4 vCPU, 8GB RAM"),
    3: Product(id=3, name="Distributed Block Storage 100GB", category="Storage", price=10.0, stock=200, description="NVMe SSD replicated storage"),
    4: Product(id=4, name="Managed Database Instance", category="Database", price=45.0, stock=15, description="High availability PostgreSQL instance"),
}

@app.get("/healthz", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "healthy", "service": "catalog-service", "timestamp": datetime.datetime.utcnow().isoformat()}

@app.get("/ready", status_code=status.HTTP_200_OK)
def readiness_check():
    return {"ready": True}

@app.get("/api/v1/products", response_model=List[Product])
def list_products(category: Optional[str] = Query(None)):
    if category:
        return [p for p in CATALOG_DB.values() if p.category.lower() == category.lower()]
    return list(CATALOG_DB.values())

@app.get("/api/v1/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    product = CATALOG_DB.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.post("/api/v1/products", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate):
    new_id = max(CATALOG_DB.keys(), default=0) + 1
    new_product = Product(id=new_id, **product.model_dump())
    CATALOG_DB[new_id] = new_product
    return new_product

@app.patch("/api/v1/products/{product_id}/deduct-stock")
def deduct_stock(product_id: int, quantity: int = Query(..., gt=0)):
    product = CATALOG_DB.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.stock < quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    product.stock -= quantity
    return {"id": product.id, "new_stock": product.stock}

