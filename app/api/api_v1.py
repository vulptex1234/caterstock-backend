from fastapi import APIRouter
from app.api.endpoints import auth, inventory

api_router = APIRouter()
 
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"]) 