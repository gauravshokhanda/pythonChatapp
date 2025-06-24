from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/ping")
async def user_ping():
    return {"message": "User service running"}
