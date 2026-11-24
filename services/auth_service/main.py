from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
import datetime
import os

SECRET_KEY = os.getenv("JWT_SECRET", "super-secret-production-grade-key-xyz")
ALGORITHM = "HS256"

app = FastAPI(
    title="Auth Microservice",
    description="Cloud-native authentication and identity verification service",
    version="1.0.0"
)

security = HTTPBearer()

class UserRegister(BaseModel):
    username: str
    password: str
    email: str

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in_hours: int

USERS_DB = {}

@app.get("/healthz", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "healthy", "service": "auth-service", "timestamp": datetime.datetime.utcnow().isoformat()}

@app.get("/ready", status_code=status.HTTP_200_OK)
def readiness_check():
    return {"ready": True}

@app.post("/api/v1/auth/register", status_code=status.HTTP_201_CREATED)
def register(user: UserRegister):
    if user.username in USERS_DB:
        raise HTTPException(status_code=400, detail="Username already registered")
    USERS_DB[user.username] = {"password": user.password, "email": user.email}
    return {"message": "User registered successfully", "username": user.username}

@app.post("/api/v1/auth/login", response_model=TokenResponse)
def login(credentials: UserLogin):
    user = USERS_DB.get(credentials.username)
    if not user or user["password"] != credentials.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    
    payload = {
        "sub": credentials.username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        "iat": datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return TokenResponse(access_token=token, token_type="bearer", expires_in_hours=24)

@app.get("/api/v1/auth/verify")
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return {"valid": True, "username": payload["sub"]}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

