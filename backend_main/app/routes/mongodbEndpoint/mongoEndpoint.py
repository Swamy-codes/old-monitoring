



from fastapi import APIRouter, HTTPException, Request, Depends
from typing import List
from database.mongodb import get_mongodb_db

router = APIRouter()

async def get_collection(request: Request):
    db = get_mongodb_db(request.app)
    return db["Elno_SensorDataActive"]

# async def get_collection(request: Request):
#     db = get_mongodb_db(request.app)
#     collection = db["Elno_SensorDataActive"] 
#     return collection


@router.get("/mongoDataTemp")
async def mongoDataLevel(collection=Depends(get_collection)):
    try:
        cursor = collection.find({"L1Name": "MCV-450", "signalname": {"$regex": "Temp", "$options": "i"}})
        documents = await cursor.to_list(length=None)

        if documents:
            for doc in documents:
                doc["_id"] = str(doc["_id"])  # Convert ObjectId to string for JSON serialization
        
        return {"data": documents}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch data: {str(e)}")
    
@router.get("/mongoDataLevel")
async def mongoDataLevel(collection=Depends(get_collection)):
    try:
        cursor = collection.find({"L1Name": "MCV-450", "signalname": {"$regex": "Level", "$options": "i"}})
        documents = await cursor.to_list(length=None)
        
        if documents:
            for doc in documents:
                doc["_id"] = str(doc["_id"]) 
        
        return {"data": documents}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch data: {str(e)}")
    
@router.get("/mongoDataPressure")
async def mongoDataLevel(collection=Depends(get_collection)):
    try:
        cursor = collection.find({"L1Name": "MCV-450", "signalname": {"$regex": "Pressure", "$options": "i"}})
        documents = await cursor.to_list(length=None)
        
        if documents:
            for doc in documents:
                doc["_id"] = str(doc["_id"]) 
        
        return {"data": documents}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch data: {str(e)}")
    
@router.get("/mongoDataEnergy")
async def mongoDataLevel(collection=Depends(get_collection)):
    try:
        cursor = collection.find({"L1Name": "MCV-450", "signalname": {"$regex": "Energy", "$options": "i"}})
        documents = await cursor.to_list(length=None)
        
        if documents:
            for doc in documents:
                doc["_id"] = str(doc["_id"]) 
        
        return {"data": documents}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch data: {str(e)}")
    

@router.get("/mongoDataVib")
async def mongoDataLevel(collection=Depends(get_collection)):
    try:
        cursor = collection.find({"L1Name": "MCV-450", "signalname": {"$regex": "Vib", "$options": "i"}})
        documents = await cursor.to_list(length=None)
        
        if documents:
            for doc in documents:
                doc["_id"] = str(doc["_id"]) 
        
        return {"data": documents}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch data: {str(e)}")

