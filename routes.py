from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .security import verify_password, create_access_token, hash_password

router = APIRouter(prefix="/api/auth", tags=["auth"])
USERS = {"admin": {"password": hash_password("admin123"), "role": "ADMIN"}, "operator": {"password": hash_password("operator123"), "role": "OPERATOR"}, "analyst": {"password": hash_password("analyst123"), "role": "ANALYST"}}

class Login(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(data: Login):
    user = USERS.get(data.username)
    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(401, "Invalid username or password")
    return {"access_token": create_access_token(data.username, user["role"]), "token_type": "bearer", "role": user["role"]}
