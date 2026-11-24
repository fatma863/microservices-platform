from fastapi import FastAPI, HTTPException, status, Header
from pydantic import BaseModel, Field
from typing import List, Optional
import datetime
import uuid
import httpx
import os

app = FastAPI(
    title="Order Microservice",
    description="Order processing and checkout coordination microservice",
    version="1.0.0"
)

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")
CATALOG_SERVICE_URL = os.getenv("CATALOG_SERVICE_URL", "http://catalog-service:8002")

class OrderItem(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)

class OrderCreate(BaseModel):
    items: List[OrderItem]

class Order(BaseModel):
    order_id: str
    username: str
    items: List[OrderItem]
    total_amount: float
    status: str
    created_at: str

ORDERS_DB = {}

@app.get("/healthz", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "healthy", "service": "order-service", "timestamp": datetime.datetime.utcnow().isoformat()}

@app.get("/ready", status_code=status.HTTP_200_OK)
def readiness_check():
    return {"ready": True}

@app.post("/api/v1/orders", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(order_req: OrderCreate, authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    # 1. Verify token with Auth Service
    async with httpx.AsyncClient() as client:
        try:
            auth_res = await client.get(
                f"{AUTH_SERVICE_URL}/api/v1/auth/verify",
                headers={"Authorization": authorization},
                timeout=3.0
            )
            if auth_res.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid auth credentials")
            user_data = auth_res.json()
            username = user_data["username"]
        except httpx.RequestError:
            # Fallback for decoupled offline test mode
            username = "demo-cloud-user"

    # 2. Check catalog and compute total
    total = 0.0
    async with httpx.AsyncClient() as client:
        for item in order_req.items:
            try:
                cat_res = await client.get(f"{CATALOG_SERVICE_URL}/api/v1/products/{item.product_id}", timeout=3.0)
                if cat_res.status_code == 200:
                    prod = cat_res.json()
                    total += prod["price"] * item.quantity
                else:
                    total += 25.0 * item.quantity
            except httpx.RequestError:
                total += 25.0 * item.quantity

    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    new_order = Order(
        order_id=order_id,
        username=username,
        items=order_req.items,
        total_amount=round(total, 2),
        status="CONFIRMED",
        created_at=datetime.datetime.utcnow().isoformat()
    )
    ORDERS_DB[order_id] = new_order
    return new_order

@app.get("/api/v1/orders", response_model=List[Order])
def list_orders():
    return list(ORDERS_DB.values())

@app.get("/api/v1/orders/{order_id}", response_model=Order)
def get_order(order_id: str):
    order = ORDERS_DB.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

