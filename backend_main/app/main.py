import asyncio
from fastapi import FastAPI, Depends, HTTPException, status, Request
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter
from database.mongodb import startup_mongodb, shutdown_mongodb
from database.postgres import get_postgres_pool, startup_postgres, shutdown_postgres
from routes.postgresEndpoint import postgresEndpoints
from routes.mongodbEndpoint import mongoEndpoint,mtlinki
from database.dataCollector import initialize_collection, background_monitoring_tasks, create_monitoring_tables, machine_signal_append, run_daily_task
from database.statuscollector import sync_machine_status
from routes import auth

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from routes.auth import create_access_token, decode_token
from routes import machine_issues

def start_scheduler(app: FastAPI):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(background_monitoring_tasks, 'interval', seconds=60, args=[app])
    scheduler.add_job(run_daily_task, 'cron', hour=0, minute=0, args=[app])
    scheduler.add_job(sync_machine_status, 'interval', seconds=10)
    scheduler.start()
 

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        
        await startup_postgres(app)  
        await startup_mongodb(app)
        await get_postgres_pool(app)
        initialize_collection(app)
        await create_monitoring_tables(app)
        await machine_signal_append()
        # asyncio.create_task(background_monitoring_tasks(app))       # Start the background monitoring tasks


        0
        start_scheduler(app)
        yield
    except Exception as e:
        print(f"Error in startup process: {e}")
        raise

    finally:
        try:
            await shutdown_postgres(app)
            await shutdown_mongodb(app)
        except Exception as e:
            print(f"Error during shutdown: {e}")


app = FastAPI(lifespan=lifespan)
              
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your actual frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST","PUT"],
    allow_headers=["Content-Type"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

fake_users_db = {
    "admin": {
        "username": "Admin",
        "password": "1234",
        "role": "admin"
    },
    "supervisor": {
        "username": "Supervisor",
        "password": "1234",
        "role": "supervisor"
    }
}


router = APIRouter(prefix="/auth")  
app.include_router(postgresEndpoints.router)


app.include_router(mongoEndpoint.router)
app.include_router(mtlinki.router)
app.include_router(auth.router)
app.include_router(machine_issues.router)
@app.get("/")
async def root():
    return {"message": "Welcome to the Monitoring dashboard application!"}


@app.post("/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user["username"], "role": user["role"]})
    return {"access_token": token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload

@app.get("/admin/data")
async def admin_data(user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return {"data": "This is secret admin data!"}

# @app.get("/start-monitoring")
# async def start_monitoring(background_tasks: BackgroundTasks):
#     background_tasks.add_task(background_monitoring_tasks, app)
#     return {"message": "Monitoring started."}

# @app.get("/api/temperature-data")
# async def get_temperature_data(limit: int = 2):
#     try:
#         conn = await connect_to_postgres()
#         query = "SELECT l1name, signalname, updatedate, value, status, ist_updatedate FROM temp_monitoring LIMIT $1"
#         rows = await conn.fetch(query, limit)
#         await conn.close()

#         # Convert rows to JSON serializable format
#         data = [dict(row) for row in rows]
#         return {"data": data}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
