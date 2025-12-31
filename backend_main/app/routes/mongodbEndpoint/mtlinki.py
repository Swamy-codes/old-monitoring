from fastapi import APIRouter
from database.mtlinkmongo import db

router = APIRouter()

@router.get("/l1-pool-opened")
def get_l1_pool_opened():
    data = list(db["L1_Pool_Opened"].find({}, {"_id": 0}))
    return {"status": "success", "data": data}
