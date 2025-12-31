import asyncio
from datetime import date, datetime
from io import BytesIO 
from fastapi import APIRouter, FastAPI,  HTTPException, Query, Request, Response, WebSocket, WebSocketDisconnect, logger,UploadFile, File, Form
from typing import List, Optional

from fastapi.responses import StreamingResponse
from models import MachineName, SignalName
from database.postgres import get_postgres_pool
import asyncio
from asyncio import Lock
import json
from decimal import Decimal
import logging
from pydantic import BaseModel,EmailStr

logger = logging.getLogger(__name__)
class OperatorEmailCreate(BaseModel):
    machine_name: str
    operator_name: str
    email: EmailStr
class SupervisorEmailOut(BaseModel):
    id: int
    name: str
    email: EmailStr
class SupervisorEmailUpdate(BaseModel):  
    name: Optional[str] = None
    email: Optional[EmailStr] = None
class MachineDataCreate(BaseModel):
    machine_name: str
    tc: float
    gc: float
    dc: float
    qr: float
class Threshold(BaseModel):
    id: int
    l1name: str
    signalname: str
    component: str
    low: float
    normalmin: float
    normalmax: float
    high: float
class OperatorEmailUpdate(BaseModel):
    machine_name: Optional[str]
    operator_name: Optional[str]
    email: Optional[EmailStr]

class OperatorEmailOut(BaseModel):
    id: int
    machine_name: str
    operator_name: str
    email: EmailStr
class ThresholdUpdate(BaseModel):
    low: float
    normalmin: float
    normalmax: float
    high: float
class OEEData(BaseModel):
    machine_name: str
    created_date: str
    tc: float
    gc: float
    qr: float
    run_minutes: float
    availability: float
    performance: float
    quality: Optional[float]  # Allow null
    oee: Optional[float]      #
router = APIRouter()
app = FastAPI()
class MachineStatus(BaseModel):
    machine_name: str
    value: str
    updated_at: datetime
class PDFUpload(BaseModel):
    machine_name: str
    description: Optional[str] = None

class PDFDocumentOut(BaseModel):
    id: int
    machine_name: str
    file_name: str
    file_size: int
    upload_timestamp: datetime
    category: Optional[str]  # ✅ Accepts NULL / None from DB

table_names = {
    "Temperature": 'Temperature',
    "Pressure": 'Pressure',
    "Level": 'Level',
    "Vibration": 'Vibration',
    "Energy": 'Energy',
}
# GET: Fetch all threshold data
@router.post("/machine-documents/upload/", response_model=PDFDocumentOut)
async def upload_pdf(
    request: Request,
    machine_name: str = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    category: str = Form(...)
):
    try:
        # Validate file
        if not (file.content_type == "application/pdf" or 
                file.filename.lower().endswith('.pdf')):
            raise HTTPException(400, "Only PDF files allowed")

        # Read in chunks to handle large files
        CHUNK_SIZE = 1024 * 1024  # 1MB
        chunks = []
        size = 0
        while content := await file.read(CHUNK_SIZE):
            chunks.append(content)
            size += len(content)
        
        if size == 0:
            raise HTTPException(400, "Empty file")
            
        file_data = b''.join(chunks)

        pool = await get_postgres_pool(request.app)
        async with pool.acquire() as conn:
            async with conn.transaction():
                result = await conn.fetchrow(
    """
    INSERT INTO machine_documents 
    (machine_name, file_name, file_data, file_size, mime_type, additional_metadata, category)
    VALUES ($1, $2, $3, $4, $5, $6, $7)
    RETURNING id, machine_name, file_name, file_size, upload_timestamp, category
    """,
    machine_name,             # $1
    file.filename,            # $2
    file_data,                # $3
    size,                     # $4
    "application/pdf",        # $5
    json.dumps({"description": description}) if description else None,  # $6
    category                  # $7
)

                return dict(result)
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {type(e).__name__}: {str(e)}")
        raise HTTPException(500, f"Upload failed: {str(e)}")

@router.get("/machine-documents/", response_model=List[PDFDocumentOut])
async def get_all_documents(
    request: Request,
    machine_name: Optional[str] = Query(None)
):
    try:
        pool = await get_postgres_pool(request.app)
        async with pool.acquire() as conn:
            if machine_name:
                query = """
                    SELECT id, machine_name, file_name, file_size, upload_timestamp, category
                    FROM machine_documents
                    WHERE machine_name = $1
                    ORDER BY upload_timestamp DESC
                """
                rows = await conn.fetch(query, machine_name)
            else:
                query = """
                    SELECT id, machine_name, file_name, file_size, upload_timestamp, category
                    FROM machine_documents
                    ORDER BY upload_timestamp DESC
                """
                rows = await conn.fetch(query)

        return [dict(row) for row in rows]

    except Exception as e:
        import traceback
        logger.error("Error in get_all_documents:")
        logger.error(traceback.format_exc())
        raise HTTPException(500, f"Could not fetch documents: {str(e)}")
@router.get("/machine-documents/{doc_id}/download")
async def download_pdf(doc_id: int, request: Request):
    pool = await get_postgres_pool(request.app)
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT file_name, file_data FROM machine_documents WHERE id = $1",
            doc_id
        )
        if not row:
            raise HTTPException(404, "Document not found")

        return StreamingResponse(
            BytesIO(row["file_data"]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={row['file_name']}"}
        )
@router.delete("/machine-documents/{document_id}")
async def delete_pdf(request: Request, document_id: int):
    try:
        pool = await get_postgres_pool(request.app)
        async with pool.acquire() as conn:
            async with conn.transaction():
                # First check if document exists
                exists = await conn.fetchval(
                    "SELECT 1 FROM machine_documents WHERE id = $1",
                    document_id
                )
                if not exists:
                    raise HTTPException(status_code=404, detail="Document not found")
                    
                await conn.execute(
                    "DELETE FROM machine_documents WHERE id = $1",
                    document_id
                )
                
                return {"message": "Document deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting PDF: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete document")
@router.get("/thresholds", response_model=List[Threshold])
async def get_all_thresholds(request: Request):
    try:
        pool = await get_postgres_pool(request.app)
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM Thresholds ORDER BY id")
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching thresholds: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch threshold data")
    
@router.get("/operator_email", response_model=List[dict])  # Adjust the response_model as needed
async def get_all_operators(request: Request):
    try:
        pool = await get_postgres_pool(request.app)
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM operator_email ORDER BY id")
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching operator data: {str(e)}")

@router.get("/supervisor_email", response_model=List[dict])  # Adjust the response_model as needed
async def get_all_operators(request: Request):
    try:
        pool = await get_postgres_pool(request.app)
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM supervisor_email ORDER BY id")
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching operator data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch operator data")
    
@router.get("/alert_entry", response_model=List[dict])  
async def get_all_emailentry(request: Request):
    try:
        pool = await get_postgres_pool(request.app)
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM alert_entry ORDER BY id")
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching operator data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch operator data")
    
@router.put("/operators_email/{id}", response_model=OperatorEmailOut)
async def update_operator(request: Request, id: int, payload: OperatorEmailUpdate):
    try:
        pool = await get_postgres_pool(request.app)
        async with pool.acquire() as conn:
            async with conn.transaction():
                # Check if operator exists
                existing = await conn.fetchrow(
                    "SELECT * FROM operator_email WHERE id = $1", id
                )
                if not existing:
                    raise HTTPException(status_code=404, detail="Operator not found")

                # Preserve old values if fields are not updated
                machine_name = payload.machine_name or existing["machine_name"]
                operator_name = payload.operator_name or existing["operator_name"]
                email = payload.email or existing["email"]

                # Perform update
                await conn.execute("""
                    UPDATE operator_email
                    SET machine_name = $1,
                        operator_name = $2,
                        email = $3
                    WHERE id = $4
                """, machine_name, operator_name, email, id)

                # Return updated row
                updated = await conn.fetchrow(
                    "SELECT * FROM operator_email WHERE id = $1", id
                )
                return dict(updated)
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating operator: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update operator data")
    
@router.put("/supervisors_emailupdate/{id}", response_model=SupervisorEmailOut)
async def update_supervisor(request: Request, id: int, payload: SupervisorEmailUpdate):
    try:
        pool = await get_postgres_pool(request.app)
        async with pool.acquire() as conn:
            async with conn.transaction():
                # Check if supervisor exists
                existing = await conn.fetchrow(
                    "SELECT * FROM supervisor_email WHERE id = $1", id
                )
                if not existing:
                    raise HTTPException(status_code=404, detail="Supervisor not found")

                # Preserve old values if fields are not updated
                name = payload.name or existing["name"]
                email = payload.email or existing["email"]

                # Perform update
                await conn.execute("""
                    UPDATE supervisor_email
                    SET name = $1,
                        email = $2
                    WHERE id = $3
                """, name, email, id)

                # Return updated row
                updated = await conn.fetchrow(
                    "SELECT * FROM supervisor_email WHERE id = $1", id
                )
                return dict(updated)
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating supervisor: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update supervisor data")
    
@router.post("/supervisors_emailnew", response_model=SupervisorEmailOut)
async def create_supervisor(request: Request, payload: SupervisorEmailUpdate):
    try:
        pool = await get_postgres_pool(request.app)
        async with pool.acquire() as conn:
            async with conn.transaction():
                result = await conn.fetchrow("""
                    INSERT INTO supervisor_email (name, email)
                    VALUES ($1, $2)
                    RETURNING id, name, email
                """, payload.name, payload.email)

                return dict(result)

    except Exception as e:
        logger.error(f"Error creating supervisor: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create supervisor entry")
   
@router.post("/operators_emailnew", response_model=OperatorEmailOut)
async def create_operator(request: Request, payload: OperatorEmailCreate):

    try:
        pool = await get_postgres_pool(request.app)
        async with pool.acquire() as conn:
            async with conn.transaction():
                # Insert new record
                row = await conn.fetchrow("""
                    INSERT INTO operator_email (machine_name, operator_name, email)
                    VALUES ($1, $2, $3)
                    RETURNING *
                """, payload.machine_name, payload.operator_name, payload.email)

                if not row:
                    raise HTTPException(status_code=500, detail="Insert failed")

                return dict(row)

    except Exception as e:
        logger.error(f"Error creating operator: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create operator")
# PUT: Update specific threshold row
@router.put("/thresholds/{id}", response_model=Threshold)
async def update_threshold(request: Request, id: int, payload: ThresholdUpdate):
    try:
        pool = await get_postgres_pool(request.app)
        async with pool.acquire() as conn:
            # Start a transaction
            async with conn.transaction():
                # Check if exists
                existing = await conn.fetchrow(
                    "SELECT * FROM thresholds WHERE id = $1", id  # Note: lowercase 'thresholds' if that's your table name
                )
                if not existing:
                    raise HTTPException(status_code=404, detail="Threshold entry not found")

                # Update query
                await conn.execute("""
                    UPDATE thresholds
                    SET low = $1, normalmin = $2, normalmax = $3, high = $4
                    WHERE id = $5
                """, 
                payload.low, payload.normalmin, payload.normalmax, payload.high, id)

                # Return updated row
                updated = await conn.fetchrow(
                    "SELECT * FROM thresholds WHERE id = $1", id
                )
                return dict(updated)
                
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Error updating threshold: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update threshold data")

@router.get("/oee-data", response_model=List[OEEData])
async def get_oee_data(request: Request):
    query = """
    WITH raw_status AS (
        SELECT
            LOWER(machine_name) AS machine_name,
            updated_at,
            value,
            LEAD(value) OVER (PARTITION BY machine_name ORDER BY updated_at) AS next_value,
            LEAD(updated_at) OVER (PARTITION BY machine_name ORDER BY updated_at) AS next_time
        FROM machine_status_log
    ),
    status_durations AS (
        SELECT
            machine_name,
            DATE(updated_at) AS created_date,
            updated_at,
            next_time
        FROM raw_status
        WHERE value = 'OPERATE' AND next_value = 'DISCONNECT'
    ),
    operate_durations AS (
        SELECT
            machine_name,
            created_date,
            SUM(EXTRACT(EPOCH FROM (next_time - updated_at)) / 60.0)::numeric AS run_minutes
        FROM status_durations
        GROUP BY machine_name, created_date
    ),
    production_data AS (
        SELECT
            LOWER(machine_name) AS machine_name,
            created_date,
            SUM(tc)::numeric AS tc,
            SUM(gc)::numeric AS gc,
            AVG(qr)::numeric AS qr
        FROM oee_operator
        GROUP BY machine_name, created_date
    )
    SELECT
        p.machine_name,
        p.created_date::text,
        p.tc,
        p.gc,
        ROUND(p.qr::numeric, 2) AS qr,
        ROUND(COALESCE(o.run_minutes, 0), 2) AS run_minutes,
        ROUND(COALESCE(o.run_minutes, 0) / 480.0, 2) AS availability,
        ROUND(
            CASE 
                WHEN COALESCE(o.run_minutes, 0) > 0 
                THEN p.tc::numeric / o.run_minutes
                ELSE 0 
            END, 2
        ) AS performance,
        ROUND(p.gc::numeric / NULLIF(p.tc, 0), 2) AS quality,
        ROUND(
            (COALESCE(o.run_minutes, 0) / 480.0) *
            (CASE 
                WHEN COALESCE(o.run_minutes, 0) > 0 THEN p.tc::numeric / o.run_minutes
                ELSE 0 
            END) *
            (p.gc::numeric / NULLIF(p.tc, 0)),
        2) AS oee
    FROM production_data p
    LEFT JOIN operate_durations o 
        ON p.machine_name = o.machine_name 
       AND p.created_date = o.created_date
    ORDER BY p.created_date DESC;
    """
    try:
        pool = await get_postgres_pool(request.app)
        async with pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching OEE data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))
@router.post("/machine-data/")
async def create_machine_data(request: Request, data: MachineDataCreate):
    try:
        pool = await get_postgres_pool(request.app)
        async with pool.acquire() as conn:
            insert_query = """
                INSERT INTO oee_operator (machine_name, tc, gc, dc, qr)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id;
            """
            inserted = await conn.fetchrow(
                insert_query,
                data.machine_name,
                data.tc,
                data.gc,
                data.dc,
                data.qr
            )
            return {"message": "Data inserted successfully", "id": inserted["id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/machineName", response_model=List[MachineName])
# request: Request represents the incoming HTTP request, give access to details about the request- headers, query parameters, application state.
async def machineNameData(request: Request):
    try:

        pool = await get_postgres_pool(request.app)
        async with pool.acquire() as conn:
            # sync with request.app.state.postgres_pool.acquire() as conn:
            machineNameQuery="SELECT DISTINCT L1name AS selected_machine_name FROM Temperature"
            fetchedMachineName = await conn.fetch(machineNameQuery)
            machineNames = [MachineName(selected_machine_name = record['selected_machine_name']) for record in fetchedMachineName]
            return machineNames
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed to fetcg machine name: {str(e)}")


patterns = {
            "Temperature": r'%_Temp%', 
            "Energy": r'%_Energy%',     
            "Level": r'%_Level%',      
            "Pressure": r'%_Pressure%',   
            "Vibration": [r'Mtr_%_X', r'Mtr_%_Y', r'Spin_%_X', r'Spin_%_Y']  
        }

def serialize_custom(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()  
    elif isinstance(obj, date):
        return obj.isoformat() 
    elif isinstance(obj, Decimal):
        return float(obj)  
    raise TypeError(f"Type {type(obj).__name__} not serializable")


# app.state.selected_machine_name = None
lock = Lock()

@router.websocket("/ws/{selected_machine_name}/{selectedComponent}")
async def websocket_endpoint(websocket: WebSocket, selected_machine_name: str, selectedComponent: str):
    await websocket.accept()
    pattern = patterns.get(selectedComponent)
    
    if pattern is None:
        await websocket.close(code=4000)
        return

    # Set the machine name in app state
    app.state.selected_machine_name = selected_machine_name
    last_sent_machine = selected_machine_name

    try:
        while True:
            async with lock:
                current_machine_name = app.state.selected_machine_name

                if current_machine_name != last_sent_machine:
                    # logger.info(f"Machine name updated to: {current_machine_name}")
                    await websocket.send_text(json.dumps({"status": "Machine changed", "machine": current_machine_name}))
                    last_sent_machine = current_machine_name

                # Query the database for the current machine
                pool = await get_postgres_pool(websocket.app)
                async with pool.acquire() as conn:
                    if isinstance(pattern, list):
                        patterns_query = " OR ".join(f"signalname LIKE ${i+2}" for i in range(len(pattern)))
                        query = f"""
                            SELECT * 
                            FROM active 
                            WHERE l1name = $1 
                            AND ({patterns_query})
                            ORDER BY signalname ASC
                        """
                        values = (current_machine_name, *pattern)
                    else:
                        query = """
                            SELECT * 
                            FROM active 
                            WHERE l1name = $1 
                            AND signalname LIKE $2
                            ORDER BY signalname ASC
                        """
                        values = (current_machine_name, pattern)
                    
                    rows = await conn.fetch(query, *values)
                    # logger.info(f"Query values: {values}")
                    
                    if rows:
                        results = [dict(row) for row in rows] 

                        # logger.info(f"Query result: {results[0]}")

                        for result in results:
                            for key, value in result.items():
                                if isinstance(value, datetime):
                                    result[key] = value.isoformat()
                                elif isinstance(value, Decimal):
                                    result[key] = float(value)
                    else:
                        results = []
                        logger.info(f"No data found for machine: {current_machine_name}")

                    await websocket.send_text(json.dumps({"Livedata": results}, default=serialize_custom))


            await asyncio.sleep(5)  # Delay between polling
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        await websocket.close(code=4000)
        logger.error(f"Error in WebSocket connection: {e}")

@router.get("/signalName/{selected_machine_name}/{selectedComponent}", response_model=List[SignalName])
async def signalNameData(request: Request,
                         selected_machine_name: str, 
                          selectedComponent: str,):
    table_name = table_names.get(selectedComponent.capitalize())
    if not table_name:
        raise HTTPException(status_code=400, detail="Invalid parameter")
    try:
        pool = await get_postgres_pool(request.app)
        async with pool.acquire() as conn:

            signalNameQuery = f""" 
            SELECT DISTINCT signalname AS selected_signal_name 
            FROM {table_name} 
            WHERE L1name = $1
            """
            fetchedSignalName = await conn.fetch(signalNameQuery, selected_machine_name)
            signalNames = [SignalName(selected_signal_name=record['selected_signal_name']) for record in fetchedSignalName]

            return signalNames
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed to fetcg machine name: {str(e)}")

# class MultipleDatesRequest(BaseModel):
#     multiple_dates: Optional[List[date]] = None
@router.get("/machine-status-history/{machine_name}")
async def get_status_history(request: Request, machine_name: str):
    try:
        pool = await get_postgres_pool(request.app)
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT machine_name, value, updated_at
                FROM machine_status_log
                WHERE TRIM(LOWER(machine_name)) = TRIM(LOWER($1))
                ORDER BY updated_at ASC
            """, machine_name)
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/machineData/{selected_machine_name}/{selectedComponent}")
async def get_machine_data(request: Request,
                           selected_machine_name: str, 
                           selectedComponent: str,
                           signal_name: str,
                           start_date: date,
                           end_date: Optional[date] = None,
                           multiple_dates: Optional[List[date]] = None,     
                           granularity_str: Optional[str] = None):
    
    # Ensure selectedComponent is valid
    table_name = table_names.get(selectedComponent.capitalize())
    if not table_name:
        raise HTTPException(status_code=400, detail="Invalid parameter")
    
    # Ensure required parameters are provided
    if not selected_machine_name or not selectedComponent:
        raise HTTPException(status_code=400, detail="Missing required parameters")
    
    # Validate granularity_str
    if granularity_str is None:
        granularity_str = "second"  # or some default value or raise an error

    granularity_str = granularity_str.lower()

    # Generate the query based on granularity
    if granularity_str == "hour":
        query = f""" 
            SELECT date_trunc('hour', ist_updatedate) as hour,
            avg(value) as value
            FROM {table_name} 
            WHERE L1name = $1 
            AND signalname = $2
            """
        if start_date and end_date:
            query += " AND ist_updatedate BETWEEN $3 AND $4"
            query_params = [selected_machine_name, signal_name, start_date, end_date]

        elif multiple_dates:
            query += " AND ist_updatedate IN (" + ",".join(["$" + str(i+3) for i in range(len(multiple_dates))]) + ")"
            query_params = [selected_machine_name, signal_name, multiple_dates]

        #     type i for i in multiple_dates == date:
        #         # check is all elements in multiple dates in date format
        #          query += " AND  i == ist_updatedate for i in $3"
        #          query_params = [selected_machine_name, signal_name, multiple_dates]
        
        else:
            query += " AND CAST(ist_updatedate AS DATE) = $3"
            query_params = [selected_machine_name, signal_name, start_date]
        query += " GROUP BY hour ORDER BY hour"
    
    elif granularity_str == "minute":
        query = f""" 
            SELECT date_trunc('minute', ist_updatedate) as minute,
            avg(value) as value
            FROM {table_name} 
            WHERE L1name = $1 
            AND signalname = $2 
            """  
        if start_date and end_date:
            query += " AND ist_updatedate BETWEEN $3 AND $4"
            query_params = [selected_machine_name, signal_name, start_date, end_date]

        elif multiple_dates:
                query += " AND ist_updatedate IN (" + ",".join(["$" + str(i+3) for i in range(len(multiple_dates))]) + ")"
                query_params = [selected_machine_name, signal_name, multiple_dates]

        else:
            query += " AND CAST(ist_updatedate AS DATE) = $3"
            query_params = [selected_machine_name, signal_name, start_date]
        query += " GROUP BY minute ORDER BY minute"

    else:  # Default to "second" if granularity_str is not recognized
        query = f"""
            SELECT date_trunc('second', ist_updatedate) as second,
            avg(value) as value 
            FROM {table_name} 
            WHERE L1name = $1 
            AND signalname = $2
          """    
        if start_date and end_date:
            query += " AND ist_updatedate BETWEEN $3 AND $4"
            query_params = [selected_machine_name, signal_name, start_date, end_date]
        elif multiple_dates:
                query += " AND ist_updatedate IN (" + ",".join(["$" + str(i+3) for i in range(len(multiple_dates))]) + ")"
                query_params = [selected_machine_name, signal_name, multiple_dates]

        else:
            query += " AND CAST(ist_updatedate AS DATE) = $3"
            query_params = [selected_machine_name, signal_name, start_date]
        query += " GROUP BY second ORDER BY second"
    
    try:
        pool = await get_postgres_pool(request.app)
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, *query_params)

        # Convert rows to JSON serializable format
        machineData = [dict(row) for row in rows]
        print(len(machineData))
        return {"machineData": machineData}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
