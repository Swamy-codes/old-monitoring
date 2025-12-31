# #Monitoring and storing results in IST format(Pressure,level_indicator,temperatures,vibration)
# from fastapi import FastAPI, HTTPException
# from pymongo import MongoClient
# from datetime import datetime, timedelta
# import asyncpg
# import uvicorn
# import asyncio
# import pytz

# # MongoDB connection details
# MONGO_URI = "mongodb://Electrono:Elno%40560066@172.18.30.150:27018/&authMechanism=DEFAULT&authSource=EFORCAST_CMTI?authSource=EFORCAST_CMTI"
# DB_NAME = "EFORCAST_CMTI"
# COLLECTION_NAME = "Elno_SensorDataActive"

# # Connect to MongoDB
# client = MongoClient(MONGO_URI)
# db = client[DB_NAME]
# collection = db[COLLECTION_NAME]

# # Example machine names and signal names
# MACHINE_NAMES = [
#     "Stallion-200",
#     "Mazak-H400",
#     "MCV-450",
#     "MONO-200",
#     "Schaublin"
# ]

# PRESSURE_SIGNAL_NAMES = [
#     "Coolant_Pressure",
#     "Lub_Pressure",
#     "Hydraulic_Pressure",
#     "Tailstock_Pressure",
#     "Chuck_Pressure"
# ]

# LEVEL_SIGNAL_NAME = [  
# "Coolant_Level",
# "Hydraulic_Level"
# ]

# VIBRATION_SPINDLE_SIGNAL_NAMES = [
#     "Spin_Front_X",
#     "Spin_Front_Y", 
#     "Spin_Rear_X",
#     "Spin_Rear_Y",   
# ]

# VIBRATION_MOTOR_SIGNAL_NAMES =[
#     "Mtr_Front_X",
#     "Mtr_Front_Y",
#     "Mtr_Rear_X",
#     "Mtr_Rear_Y"
# ]

# Temperature_SIGNAL_NAMES = [
#     "Hyd_Mtr_Temp",
#     "Spn_Back_Temp",
#     "Spn_Front_Temp",
#     "Axis_Z_Temp",
#     "Spn_Mtr_Back_Temp",
#     "Axis_X_Temp",
#     "Spn_Mtr_Front_Temp"
# ]

# # Thresholds for pressure monitoring
# PRESSURE_ALARM_THRESHOLD = 50
# PRESSURE_EMERGENCY_THRESHOLD_MIN = 30
# PRESSURE_GOOD_THRESHOLD_MIN = 6

# # Threshold for level indicator monitoring
# LEVEL_ALARM_THRESHOLD = 20

# # Thresholds for vibration monitoring
# VIBRATION_SPINDLE_ALARM_THRESHOLD = 2
# VIBRATION_SPINDLE_GOOD_THRESHOLD_MIN = 1.5

# VIBRATION_MOTOR_ALARM_THRESHOLD = 1.8
# VIBRATION_MOTOR_GOOD_THRESHOLD_MIN = 1.2

# # Thresholds for Temperature monitoring
# ALARM_DANGER_THRESHOLD = 50
# GOOD_THRESHOLD_MIN = 18

# app = FastAPI()

# # PostgreSQL connection details
# POSTGRES_HOST = "localhost"
# POSTGRES_PORT = 5432
# POSTGRES_USER = "postgres"
# POSTGRES_PASSWORD = "1234"
# POSTGRES_DB = "Monitoring1"

# # Function to create PostgreSQL tables if not exists
# async def create_postgres_tables():
#     try:
#         conn = await asyncpg.connect(
#             host=POSTGRES_HOST,
#             port=POSTGRES_PORT,
#             user=POSTGRES_USER,
#             password=POSTGRES_PASSWORD,
#             database=POSTGRES_DB
#         )

#         # Create tables if they do not exist
#         await conn.execute('''
#             CREATE TABLE IF NOT EXISTS temp_monitoring (
#                 id SERIAL PRIMARY KEY,
#                 l1name VARCHAR(255),
#                 signalname VARCHAR(255),
#                 updatedate TIMESTAMP,
#                 value NUMERIC,
#                 status VARCHAR(50),
#                 ist_updatedate TIMESTAMP,
#                 UNIQUE(l1name, signalname, updatedate)
#             )
#         ''')

#         await conn.execute('''
#             CREATE TABLE IF NOT EXISTS pressure_monitoring (
#                 id SERIAL PRIMARY KEY,
#                 l1name VARCHAR(255),
#                 signalname VARCHAR(255),
#                 updatedate TIMESTAMP,
#                 value NUMERIC,
#                 status VARCHAR(50),
#                 ist_updatedate TIMESTAMP,
#                 UNIQUE(l1name, signalname, updatedate)
#             )
#         ''')

#         await conn.execute('''
#             CREATE TABLE IF NOT EXISTS level_indicator_monitoring (
#                 id SERIAL PRIMARY KEY,
#                 l1name VARCHAR(255),
#                 signalname VARCHAR(255),
#                 updatedate TIMESTAMP,
#                 value NUMERIC,
#                 status VARCHAR(50),
#                 ist_updatedate TIMESTAMP,
#                 UNIQUE(l1name, signalname, updatedate)
#             )
#         ''')

#         await conn.execute('''
#             CREATE TABLE IF NOT EXISTS vibration_monitoring (
#                 id SERIAL PRIMARY KEY,
#                 l1name VARCHAR(255),
#                 signalname VARCHAR(255),
#                 updatedate TIMESTAMP,
#                 value NUMERIC,
#                 status VARCHAR(50),
#                 ist_updatedate TIMESTAMP,
#                 UNIQUE(l1name, signalname, updatedate)
#             )
#         ''')

#         await conn.close()
#         # print("Tables created successfully.")

#     except Exception as e:
#         print(f"Error creating tables: {e}")

# # Function to convert UTC to IST (Indian Standard Time)
# IST = pytz.timezone('Asia/Kolkata')

# # Function to convert UTC to IST (Indian Standard Time)
# def convert_utc_to_ist(utc_datetime):
#     return utc_datetime.replace(tzinfo=pytz.utc).astimezone(IST)

# # Endpoint to monitor pressures and store in both MongoDB and PostgreSQL
# async def monitor_pressures():
#     try:
#         # Connect to PostgreSQL and create table if not exists
#         await create_postgres_tables()

#         # Connect to PostgreSQL for inserting data
#         conn = await asyncpg.connect(
#             host=POSTGRES_HOST,
#             port=POSTGRES_PORT,
#             user=POSTGRES_USER,
#             password=POSTGRES_PASSWORD,
#             database=POSTGRES_DB
#         )

#         # Fetch all documents from MongoDB collection
#         cursor = collection.find({})
#         for document in cursor:
#             l1_name = document.get("L1Name", "")
#             signal_name = document.get("signalname", "")
#             value = document.get("value", 0)
#             update_date = document.get("updatedate", datetime.utcnow().replace(tzinfo=pytz.utc))

#             if l1_name in MACHINE_NAMES and signal_name in PRESSURE_SIGNAL_NAMES:
#                 # Determine status based on thresholds
#                 if value > PRESSURE_ALARM_THRESHOLD:
#                     status = "alarm"
#                 elif PRESSURE_EMERGENCY_THRESHOLD_MIN <= value <= PRESSURE_ALARM_THRESHOLD:
#                     status = "emergency"
#                 elif PRESSURE_GOOD_THRESHOLD_MIN <= value < PRESSURE_EMERGENCY_THRESHOLD_MIN:
#                     status = "good"
#                 else:
#                     # Handle unexpected case
#                     status = "unknown"

#                 try:
#                     # Convert updatedate to IST
#                     ist_update_date = convert_utc_to_ist(update_date)

                

#                     # Insert data into PostgreSQL
#                     await conn.execute('''
#                         INSERT INTO pressure_monitoring (
#                             l1name, signalname, updatedate, value, status,
#                             ist_updatedate
#                         ) VALUES ($1, $2, $3, $4, $5, $6::TIMESTAMP WITH TIME ZONE)
#                     ''', 
#                     l1_name, signal_name, update_date, value, status,
#                     ist_update_date,)

#                 except asyncpg.exceptions.UniqueViolationError:
#                     # Handle duplicate key error if needed (log, ignore, etc.)
#                     continue

#         # Close PostgreSQL connection
#         await conn.close()

#         # print(" Pressure monitoring complete.")

#     except Exception as e:
#         print(f"Error in Pressure monitoring: {e}")

#         return {"message": "Pressure monitoring complete."}


# # Endpoint to monitor level indicator and store in both MongoDB and PostgreSQL
# async def monitor_level_indicator():
#     try:
#         # Connect to PostgreSQL and create table if not exists
#         await create_postgres_tables()

#         # Connect to PostgreSQL for inserting data
#         conn = await asyncpg.connect(
#             host=POSTGRES_HOST,
#             port=POSTGRES_PORT,
#             user=POSTGRES_USER,
#             password=POSTGRES_PASSWORD,
#             database=POSTGRES_DB
#         )

#         # Fetch all documents from MongoDB collection
#         cursor = collection.find({})
#         for document in cursor:
#             l1_name = document.get("L1Name", "")
#             signal_name = document.get("signalname", "")
#             value = document.get("value")
#             update_date = document.get("updatedate", datetime.utcnow().replace(tzinfo=pytz.utc))

#             if l1_name in MACHINE_NAMES and signal_name in LEVEL_SIGNAL_NAME:
#                 # Determine status based on value
#                 if isinstance(value, (int, float)) and not (value != value):  # Check if value is NaN
#                     # Value is numeric and not NaN
#                     if value < 20:
#                         status = "alarm (refill the tank)"
#                     else:
#                         status = "normal"
#                 else:
#                     # Value is None or NaN
#                     status = "unknown"

#                 try:
#                     # Convert updatedate to IST
#                     ist_update_date = convert_utc_to_ist(update_date)

#                     # Insert data into PostgreSQL
#                     await conn.execute('''
#                         INSERT INTO level_indicator_monitoring (
#                             l1name, signalname, updatedate, value, status,
#                             ist_updatedate
#                         ) VALUES ($1, $2, $3, $4, $5, $6::TIMESTAMP WITH TIME ZONE)
#                     ''', 
#                     l1_name, signal_name, update_date, value, status,
#                     ist_update_date)

#                 except asyncpg.exceptions.UniqueViolationError:
#                     # Handle duplicate key error if needed (log, ignore, etc.)
#                     continue

#         # Close PostgreSQL connection
#         await conn.close()

#         # print("Level indicator monitoring complete.")

#     except Exception as e:
#         print(f"Error in level indicator monitoring: {e}")

   

# # Endpoint to vibration_monitoring and store in both MongoDB and PostgreSQL
# async def monitor_vibration():
#     try:
#         # Connect to PostgreSQL and create table if not exists
#         await create_postgres_tables()

#         # Connect to PostgreSQL for inserting data
#         conn = await asyncpg.connect(
#             host=POSTGRES_HOST,
#             port=POSTGRES_PORT,
#             user=POSTGRES_USER,
#             password=POSTGRES_PASSWORD,
#             database=POSTGRES_DB
#         )

# # Fetch all documents from MongoDB collection
#         cursor = collection.find({})
#         for document in cursor:
#             l1_name = document.get("L1Name", "")
#             signal_name = document.get("signalname", "")
#             value = document.get("value", 0)
#             update_date = document.get("updatedate", datetime.utcnow().replace(tzinfo=pytz.utc))

#             if l1_name in MACHINE_NAMES and signal_name in VIBRATION_SPINDLE_SIGNAL_NAMES:
#                 if value > VIBRATION_SPINDLE_GOOD_THRESHOLD_MIN :
#                     status = "NOT TOLERANCE"
#                 elif value < VIBRATION_SPINDLE_ALARM_THRESHOLD:
#                     status = "GOOD"
#                 else:
#                     status = "TOLERANCE"

            
#             if l1_name in MACHINE_NAMES and signal_name in VIBRATION_MOTOR_SIGNAL_NAMES:
#                 if value > VIBRATION_MOTOR_GOOD_THRESHOLD_MIN :
#                     status = "NOT TOLERANCE"
#                 elif value < VIBRATION_MOTOR_ALARM_THRESHOLD:
#                     status = "GOOD"
#                 else:
#                     status = "TOLERANCE"


#                 try:
#                     # Convert updatedate to IST
#                     ist_update_date = convert_utc_to_ist(update_date)

#                     # Insert data into PostgreSQL
#                     await conn.execute('''
#                         INSERT INTO vibration_monitoring (
#                             l1name, signalname, updatedate, value, status,
#                             ist_updatedate
#                         ) VALUES ($1, $2, $3, $4, $5, $6::TIMESTAMP WITH TIME ZONE)
#                     ''', 
#                     l1_name, signal_name, update_date, value, status,
#                     ist_update_date,)

#                 except asyncpg.exceptions.UniqueViolationError:
#                     # Handle duplicate key error if needed (log, ignore, etc.)
#                     continue

#         # Close PostgreSQL connection
#         await conn.close()

#         # print(" Vibration monitoring complete.")

#     except Exception as e:
#         print(f"Error in Vibration monitoring: {e}")

#         return {"message": "Vibration monitoring complete."}


# # Endpoint to monitor pressures and store in both MongoDB and PostgreSQL
# async def monitor_temperatures():
#     try:
#         # Connect to PostgreSQL and create table if not exists
#         await create_postgres_tables()

#         # Connect to PostgreSQL for inserting data
#         conn = await asyncpg.connect(
#             host=POSTGRES_HOST,
#             port=POSTGRES_PORT,
#             user=POSTGRES_USER,
#             password=POSTGRES_PASSWORD,
#             database=POSTGRES_DB
#         )

#         # Fetch all documents from MongoDB collection
#         cursor = collection.find({})
#         for document in cursor:
#             l1_name = document.get("L1Name", "")
#             signal_name = document.get("signalname", "")
#             value = document.get("value", 0)
#             update_date = document.get("updatedate", datetime.utcnow().replace(tzinfo=pytz.utc))

#             if l1_name in MACHINE_NAMES and signal_name in Temperature_SIGNAL_NAMES:
#                 # Determine status based on thresholds
#                 if value < GOOD_THRESHOLD_MIN:
#                     status = "dangerously low"
#                 elif value >= ALARM_DANGER_THRESHOLD:
#                     status = "danger"
#                 else:
#                     status = "good"

#                 try:
#                     # Convert updatedate to IST
#                     ist_update_date = convert_utc_to_ist(update_date)

#                     # Insert data into PostgreSQL
#                     await conn.execute('''
#                         INSERT INTO Temp_monitoring (
#                             l1name, signalname, updatedate, value, status,
#                             ist_updatedate
#                         ) VALUES ($1, $2, $3, $4, $5, $6::TIMESTAMP WITH TIME ZONE)
#                     ''', 
#                     l1_name, signal_name, update_date, value, status,
#                     ist_update_date,)

#                 except asyncpg.exceptions.UniqueViolationError:
#                     # Handle duplicate key error if needed (log, ignore, etc.)
#                     continue

#         # Close PostgreSQL connection
#         await conn.close()

#         # print(" Temperature monitoring complete.")

#     except Exception as e:
#         print(f"Error in Temperature monitoring: {e}")

#         return {"message": "Temperature monitoring complete."}

# # Main monitoring task function
# async def run_monitoring_tasks():
#     while True:
#         await asyncio.gather(
#             monitor_pressures(),
#             monitor_level_indicator(),
#             monitor_temperatures(),
#             monitor_vibration()
           
#         )
#         await asyncio.sleep(60)  # Adjust as per your monitoring interval

# # Start the monitoring tasks when the application starts
# async def start_monitoring_tasks():
#     await run_monitoring_tasks()

# # Start monitoring endpoint for FastAPI
# @app.get("/start-monitoring")
# async def start_monitoring():
#     asyncio.create_task(start_monitoring_tasks())
#     return {"message": "Monitoring started."}

# # Run the FastAPI server with uvicorn
# if __name__ == "__main__":
#     asyncio.run(create_postgres_tables())
#     uvicorn.run(app, host="0.0.0.0", port=8001)


#     # installations
# # ->python -m venv venv(setting python virtual envi)
# # ->pip install pytz 
# # ->pip install pydantic pymongo
# # ->pip install asyncpg
# # ->pip install fastapi uvicorn 


from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from datetime import datetime, timedelta
import asyncpg
import uvicorn
import asyncio
import pytz

# MongoDB connection details
MONGO_URI = "mongodb://Electrono:Elno%40560066@172.18.30.150:27018/&authMechanism=DEFAULT&authSource=EFORCAST_CMTI?authSource=EFORCAST_CMTI"
DB_NAME = "EFORCAST_CMTI"
COLLECTION_NAME = "Elno_SensorDataActive"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Example machine names and signal names
MACHINE_NAMES = [
    "Stallion-200",
    "Mazak-H400",
    "MCV-450",
    "Mono-200",
    "Schabulin",
    "VTC-800"
]

PRESSURE_SIGNAL_NAMES = [
    "Coolant_Pressure",
    "Lub_Pressure",
    "Hydraulic_Pressure",
    "Tailstock_Pressure",
    "Chuck_Pressure"
]

LEVEL_SIGNAL_NAME = [  
"Coolant_Level",
"Hydraulic_Level"
]

VIBRATION_SPINDLE_SIGNAL_NAMES = [
    "Spin_Front_X",
    "Spin_Front_Y", 
    "Spin_Rear_X",
    "Spin_Rear_Y",   
]

VIBRATION_MOTOR_SIGNAL_NAMES =[
    "Mtr_Front_X",
    "Mtr_Front_Y",
    "Mtr_Rear_X",
    "Mtr_Rear_Y"
]

Temperature_SIGNAL_NAMES = [
    "Hyd_Mtr_Temp",
    "Spn_Back_Temp",
    "Spn_Front_Temp",
    "Axis_Z_Temp",
    "Spn_Mtr_Back_Temp",
    "Axis_X_Temp",
    "Spn_Mtr_Front_Temp"
]

ENERGY_SIGNAL_NAMES = [
    "Machine_Energy",
    "Spindle_Energy"
]


# Thresholds for Pressure monitoring
PRESSURE_ALARM_THRESHOLD = 50
PRESSURE_EMERGENCY_THRESHOLD_MIN = 30
PRESSURE_GOOD_THRESHOLD_MIN = 6

# Threshold for Level Indicator monitoring
LEVEL_ALARM_THRESHOLD = 20

# Thresholds for Vibration monitoring
VIBRATION_SPINDLE_ALARM_THRESHOLD = 2
VIBRATION_SPINDLE_GOOD_THRESHOLD_MIN = 1.5

VIBRATION_MOTOR_ALARM_THRESHOLD = 1.8
VIBRATION_MOTOR_GOOD_THRESHOLD_MIN = 1.2


# #if table exists, else update

# #mongo query to fetch machineName and create and feed into macnames array
# machnames = [x, y,z] 
# component = [component_Temp, component_Pressure...]
# use regex to populate as per a1 to populate = create a dict compnent name object- all signls names matching regeq eq in one array
# cfor loop in macname from i:
# component_Temp = collection.find({"L1Name": macname[i], "signalname": {"$regex": "Temp", "$options": "i"}})
# compnent.append(component_Temp)
# componen[0] //component_Temp // [a1_twmp, b2_temp...] // string

# # subsignLNAMEvAL = collection.find("VALE" wHERE "signalname"{`component[0][0]`})
# # thres is an array of dict
# # component temp key's value is an array of dics
# thres =[
#      { component_Temp : 
#       [
#          {good:1}, {ok:2}
#         ], 
#         },
#      { component_Pressure: {{good:1}, {ok:2}}, },
# ]
# thres[i].good.value
# thres[0].component_Temp.value[0].good //1

# # thres = { x:[a:{a1:1, a2:2 },b:{},c:{}]}
# # thre = {a:{1,2,3}, b:{2,5,7}}
# # for i in tbname:
# #     def i():
# #     mongo-collection-initialise
# # less =< thre[i][0] : status= "danger-less" #sql inser5ryion query for status column


    
# Thresholds for Temperature monitoring
ALARM_DANGER_THRESHOLD = 50
GOOD_THRESHOLD_MIN = 18

# Thresholds for Energy monitoring
ENERGY_ALARM_THRESHOLD = 10
ENERGY_GOOD_THRESHOLD_MIN = 15

app = FastAPI()

# PostgreSQL connection details
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "1234"
POSTGRES_DB = "Monitoring1"


#check if table exists then update, else create
#Creating a table in PostgreSQL
async def create_monitoring_tables(conn, table_names):
    try:
        for table_name in table_names:
            # Drop existing sequence if needed (example, handle with care)
            # await conn.execute(f'DROP SEQUENCE IF EXISTS {table_name}_id_seq;')

            await conn.execute(f'''
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id SERIAL PRIMARY KEY,
                    l1name VARCHAR(255),
                    signalname VARCHAR(255),
                    updatedate TIMESTAMP,
                    value NUMERIC,
                    status VARCHAR(50),
                    ist_updatedate TIMESTAMP,
                    insert_date DATE DEFAULT CURRENT_DATE,
                    UNIQUE(l1name, signalname, updatedate)
                )
            ''')
    except Exception as e:
        print(f"Error creating table {table_name}: {e}")
        raise
async def create_all_monitoring_tables():
    try:
        # async with request.app.pool.state.pool.acquire() as conn:
        # Connect to PostgreSQL
        conn = await asyncpg.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database=POSTGRES_DB
        )

        # List of table names , which will be created in PostgreSQL
        table_names = [
            'temp_monitoring',
            'pressure_monitoring',
            'level_indicator_monitoring',
            'vibration_monitoring',
            'energy_monitoring',
        ]

        # Create tables
        await create_monitoring_tables(conn, table_names)
	    
        # print("TABLE CREATED SUCCESSFULLY")

    except Exception as e:
        print(f"Error creating monitoring tables: {e}")

    finally:
        if conn:
            await conn.close()


# Function to convert UTC to IST (Indian Standard Time)
IST = pytz.timezone('Asia/Kolkata')

def convert_utc_to_ist(utc_datetime):
    return utc_datetime.replace(tzinfo=pytz.utc).astimezone(IST)


# Endpoint to monitor pressures and store in PostgreSQL
async def monitor_pressures():
    try:
        # Connect to PostgreSQL and create table if not exists
        await create_all_monitoring_tables()

        # Connect to PostgreSQL for inserting data
        conn = await asyncpg.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database=POSTGRES_DB
        )

        # Fetch all documents from MongoDB collection
        cursor = collection.find({})
        for document in cursor:
            l1_name = document.get("L1Name", "")
            signal_name = document.get("signalname", "")
            value = document.get("value", 0)
            update_date = document.get("updatedate", datetime.utcnow().replace(tzinfo=pytz.utc))

            # if l1_name in macname[i] and  signal_name  in component[i]:
            # f value > thre[i,good]
            #         status = "alarm"
            if l1_name in MACHINE_NAMES and signal_name in PRESSURE_SIGNAL_NAMES:
                # Determine status based on thresholds
                if value > PRESSURE_ALARM_THRESHOLD:
                    status = "alarm"
                elif PRESSURE_EMERGENCY_THRESHOLD_MIN <= value <= PRESSURE_ALARM_THRESHOLD:
                    status = "emergency"
                elif PRESSURE_GOOD_THRESHOLD_MIN <= value < PRESSURE_EMERGENCY_THRESHOLD_MIN:
                    status = "good"
                else:
                    # Handle unexpected case
                    status = "unknown"

                try:
                    # Convert updatedate to IST
                    ist_update_date = convert_utc_to_ist(update_date)

                    # Insert data into PostgreSQL
                    await conn.execute('''
                        INSERT INTO pressure_monitoring (
                            l1name, signalname, updatedate, value, status,
                            ist_updatedate
                        ) VALUES ($1, $2, $3, $4, $5, $6::TIMESTAMP WITH TIME ZONE)
                    ''', 
                    l1_name, signal_name, update_date, value, status,
                    ist_update_date,)

                except asyncpg.exceptions.UniqueViolationError:
                    # Handle duplicate key error if needed (log, ignore, etc.)
                    continue

        # Close PostgreSQL connection
        await conn.close()

        # print(" Pressure monitoring complete.")

    except Exception as e:
        print(f"Error in Pressure monitoring: {e}")

        return {"message": "Pressure monitoring complete."}


# Endpoint to monitor level indicator and store in PostgreSQL
async def monitor_level_indicator():
    try:
        # Connect to PostgreSQL and create table if not exists
        await create_all_monitoring_tables()

        # Connect to PostgreSQL for inserting data
        conn = await asyncpg.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database=POSTGRES_DB
        )

        # Fetch all documents from MongoDB collection
        cursor = collection.find({})
        for document in cursor:
            l1_name = document.get("L1Name", "")
            signal_name = document.get("signalname", "")
            value = document.get("value")
            update_date = document.get("updatedate", datetime.utcnow().replace(tzinfo=pytz.utc))

            if l1_name in MACHINE_NAMES and signal_name in LEVEL_SIGNAL_NAME:
                # Determine status based on value
                if isinstance(value, (int, float)) and not (value != value):  # Check if value is NaN
                    # Value is numeric and not NaN
                    if value < LEVEL_ALARM_THRESHOLD:
                        status = "alarm (refill the tank)"
                    else:
                        status = "normal"
                else:
                    # Value is None or NaN
                    status = "unknown"

                try:
                    # Convert updatedate to IST
                    ist_update_date = convert_utc_to_ist(update_date)

                    # Insert data into PostgreSQL
                    await conn.execute('''
                        INSERT INTO level_indicator_monitoring (
                            l1name, signalname, updatedate, value, status,
                            ist_updatedate
                        ) VALUES ($1, $2, $3, $4, $5, $6::TIMESTAMP WITH TIME ZONE)
                    ''', 
                    l1_name, signal_name, update_date, value, status,
                    ist_update_date)

                except asyncpg.exceptions.UniqueViolationError:
                    # Handle duplicate key error if needed (log, ignore, etc.)
                    continue

        # Close PostgreSQL connection
        await conn.close()

        # print("Level indicator monitoring complete.")

    except Exception as e:
        print(f"Error in level indicator monitoring: {e}")

   

# Endpoint to vibration_monitoring and store in PostgreSQL
async def monitor_vibration():
    try:
        # Connect to PostgreSQL and create table if not exists
        await create_all_monitoring_tables()

        # Connect to PostgreSQL for inserting data
        conn = await asyncpg.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database=POSTGRES_DB
        )

# Fetch all documents from MongoDB collection
        cursor = collection.find({})
        for document in cursor:
            l1_name = document.get("L1Name", "")
            signal_name = document.get("signalname", "")
            value = document.get("value", 0)
            update_date = document.get("updatedate", datetime.utcnow().replace(tzinfo=pytz.utc))

            if l1_name in MACHINE_NAMES and signal_name in VIBRATION_SPINDLE_SIGNAL_NAMES and     VIBRATION_MOTOR_SIGNAL_NAMES :
                if value > VIBRATION_SPINDLE_GOOD_THRESHOLD_MIN :
                    status = "NOT TOLERANCE"
                elif value < VIBRATION_SPINDLE_ALARM_THRESHOLD:
                    status = "GOOD"
                elif value > VIBRATION_MOTOR_GOOD_THRESHOLD_MIN :
                    status = "NOT TOLERANCE"
                elif value < VIBRATION_MOTOR_ALARM_THRESHOLD:
                    status = "GOOD"
                else:
                    status = "TOLERANCE"


                try:
                    # Convert updatedate to IST
                    ist_update_date = convert_utc_to_ist(update_date)

                    # Insert data into PostgreSQL
                    await conn.execute('''
                        INSERT INTO vibration_monitoring (
                            l1name, signalname, updatedate, value, status,
                            ist_updatedate
                        ) VALUES ($1, $2, $3, $4, $5, $6::TIMESTAMP WITH TIME ZONE)
                    ''', 
                    l1_name, signal_name, update_date, value, status,
                    ist_update_date,)

                except asyncpg.exceptions.UniqueViolationError:
                    # Handle duplicate key error if needed (log, ignore, etc.)
                    continue

        # Close PostgreSQL connection
        await conn.close()

        # print(" Vibration monitoring complete.")

    except Exception as e:
        print(f"Error in Vibration monitoring: {e}")

        return {"message": "Vibration monitoring complete."}


# Endpoint to monitor temperture and store in PostgreSQL
async def monitor_temperatures():
    try:
        # Connect to PostgreSQL and create table if not exists
        await create_all_monitoring_tables()

        # Connect to PostgreSQL for inserting data
        conn = await asyncpg.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database=POSTGRES_DB
        )

        # Fetch all documents from MongoDB collection
        cursor = collection.find({})
        for document in cursor:
            l1_name = document.get("L1Name", "")
            signal_name = document.get("signalname", "")
            value = document.get("value", 0)
            update_date = document.get("updatedate", datetime.utcnow().replace(tzinfo=pytz.utc))

            if l1_name in MACHINE_NAMES and signal_name in Temperature_SIGNAL_NAMES:
                # Determine status based on thresholds
                if value < GOOD_THRESHOLD_MIN:
                    status = "dangerously low"
                elif value >= ALARM_DANGER_THRESHOLD:
                    status = "danger"
                else:
                    status = "good"

                try:
                    # Convert updatedate to IST
                    ist_update_date = convert_utc_to_ist(update_date)

                    # Insert data into PostgreSQL
                    await conn.execute('''
                        INSERT INTO Temp_monitoring (
                            l1name, signalname, updatedate, value, status,
                            ist_updatedate
                        ) VALUES ($1, $2, $3, $4, $5, $6::TIMESTAMP WITH TIME ZONE)
                    ''', 
                    l1_name, signal_name, update_date, value, status,
                    ist_update_date,)

                except asyncpg.exceptions.UniqueViolationError:
                    # Handle duplicate key error if needed (log, ignore, etc.)
                    continue

        # Close PostgreSQL connection
        await conn.close()

        # print(" Temperature monitoring complete.")

    except Exception as e:
        print(f"Error in Temperature monitoring: {e}")

        return {"message": "Temperature monitoring complete."}
    

# Endpoint to energy_monitoring and store in PostgreSQL
async def energy_monitoring():
    try:
        # Connect to PostgreSQL and create table if not exists
        await create_all_monitoring_tables()

        # Connect to PostgreSQL for inserting data
        conn = await asyncpg.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database=POSTGRES_DB
        )

# Fetch all documents from MongoDB collection
        cursor = collection.find({})
        for document in cursor:
            l1_name = document.get("L1Name", "")
            signal_name = document.get("signalname", "")
            value = document.get("value", 0)
            update_date = document.get("updatedate", datetime.utcnow().replace(tzinfo=pytz.utc))

            if l1_name in MACHINE_NAMES and signal_name in ENERGY_SIGNAL_NAMES:
                if value > ENERGY_GOOD_THRESHOLD_MIN :
                    status = "NOT TOLERANCE"
                elif value < ENERGY_ALARM_THRESHOLD:
                    status = "GOOD"
                else:
                    status = "TOLERANCE"

                try:
                    # Convert updatedate to IST
                    ist_update_date = convert_utc_to_ist(update_date)

                    # Insert data into PostgreSQL
                    await conn.execute('''
                        INSERT INTO energy_monitoring (
                            l1name, signalname, updatedate, value, status,
                            ist_updatedate
                        ) VALUES ($1, $2, $3, $4, $5, $6::TIMESTAMP WITH TIME ZONE)
                    ''', 
                    l1_name, signal_name, update_date, value, status,
                    ist_update_date,)

                except asyncpg.exceptions.UniqueViolationError:
                    # Handle duplicate key error if needed (log, ignore, etc.)
                    continue

        # Close PostgreSQL connection
        await conn.close()


    except Exception as e:
        print(f"Error in Energy monitoring: {e}")

        return {"message": "Energy monitoring complete."}

# Main monitoring task function 
async def run_monitoring_tasks():
    while True:
        await asyncio.gather(
            monitor_pressures(),
            monitor_level_indicator(),
            monitor_temperatures(),
            monitor_vibration(),
            energy_monitoring()
           
        )
        await asyncio.sleep(60)  # Adjust as per your monitoring interval

# Start the monitoring tasks when the application starts
async def start_monitoring_tasks():
    await run_monitoring_tasks()

# Start monitoring endpoint for FastAPI
@app.get("/start-monitoring")
async def start_monitoring():
    asyncio.create_task(start_monitoring_tasks())
    return {"message": "Monitoring started."}

# Run the FastAPI server with uvicorn
if __name__ == "__main__":
    asyncio.run(create_all_monitoring_tables())
    uvicorn.run(app, host="0.0.0.0", port=8001)
