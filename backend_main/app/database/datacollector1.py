# fetch from mongo and feed into postgres - History store  amd active daraall data

# fetch data from mongo and feed into postgres
# Monitoring and storing results in IST format
from fastapi import Request
from datetime import datetime, timezone
from .mongodb import get_mongodb_collection
import asyncio
import logging
import pytz
import re

from database.postgres import get_postgres_pool 

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

collection = None
def initialize_collection(app):
    global collection
    collection = get_mongodb_collection(app)

MACHINE_NAMES = []

COMPONENTS = {
    "Temperature": [],
    "Energy": [],
    "Level": [],
    "Pressure": [],
    "Vibration": [],
    "Others": []
}

# Thresholds for monitoring (adjust as per your requirements)
THRESHOLDS = {
    "Pressure": {
        "High": lambda x: x > 50,
        "Emergency": lambda x: 30 <= x <= 50,
        "Normal": lambda x: 0 <= x < 30,
        
    },
    "Level": {
        "Low": lambda x: x < 20,
        "Normal": lambda x: x >= 20
    },
    "Vibration": {
        "Spn_High": lambda x: x > 2,
        "Spn_Tolerance": lambda x: 1.5 <= x <= 2,
        "Spn_Normal": lambda x: 0 <= x < 1.5,
        "Mtr_High": lambda x: x > 1.8,
        "Mtr_Tolerance": lambda x: 1.2 <= x <= 1.8,
        "Mtr_Normal": lambda x: 0 <= x < 1.2
    },
    "Temperature": {
        "High": lambda x: x > 50,
        "Normal": lambda x: 18 <= x <= 50,
        "Low": lambda x: x < 18
    },
    "Energy": {
        "Normal": lambda x: 0 < x <= 10,
        "Tolerance": lambda x: 11 <= x <= 15,
        "High": lambda x: x > 15,
        "Switched_Off": lambda x: x == 0
    }
}

# Define UTC and IST timezones
UTC = pytz.utc
IST = pytz.timezone('Asia/Kolkata')

def convert_utc_to_ist(utc_datetime):
    if utc_datetime.tzinfo is None:
        # If naive, localize to UTC
        utc_datetime = pytz.utc.localize(utc_datetime)
    # Convert to IST
    return utc_datetime.astimezone(IST)


    
table_schema_template = '''
    CREATE TABLE IF NOT EXISTS {table_name} (
        id SERIAL PRIMARY KEY,
        l1name VARCHAR(255),
        signalname VARCHAR(255),
        updatedate TIMESTAMP,
        value NUMERIC,
        status VARCHAR(50),
        ist_updatedate TIMESTAMP,
        insert_date DATE DEFAULT CURRENT_DATE,
        {unique_constraints}
       
    )'''
async def create_monitoring_tables(app):
    try:
        pool = await get_postgres_pool(app)
        async with pool.acquire() as conn:
        # async with request.app.state.postgres_pool.acquire() as conn:
            active_table_schema = table_schema_template.format(
                table_name='Active',
                unique_constraints='UNIQUE (l1name, signalname)'
            )    
            await conn.execute(active_table_schema)
            logger.info("Active table created successfully.")
            for table_name in THRESHOLDS.keys():
                table_schema = table_schema_template.format(
                    table_name=table_name,
                    unique_constraints='UNIQUE (l1name, signalname, updatedate)'
                )
                await conn.execute(table_schema)
                logger.info("Monitoring tables created successfully.")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")

async def machine_signal_append():
    try:
        
        cursor = collection.find({})
        # documents = await asyncio.to_thread(list, cursor)
        documents = await cursor.to_list(length = None)
        logger.info(f"Total documents fetched from MongoDB: {len(documents)}")

        # Refined patterns for accurate matching
        patterns = {
            "Temperature": r'_Temp$', 
            "Energy": r'_Energy$',     
            "Level": r'_Level$',      
            "Pressure": r'Pressure$',    
            "Vibration": [r'^Spin_', r'^Mtr_'] 
             
        }

        for document in documents:
            l1_name = document.get("L1Name", "")
            signal_name = document.get("signalname", "").strip()

            if l1_name and l1_name not in MACHINE_NAMES:
                MACHINE_NAMES.append(l1_name)

            matched = False

            for component, pattern in patterns.items():
                if component == "Vibration":
                    if not isinstance(pattern, list):
                        logger.error(f"Pattern for 'Vibration' is expected to be a list, got {type(pattern)}")
                        continue

                    # Check if signal_name matches any pattern for "Vibration"
                    matches = any(re.search(p, signal_name, re.IGNORECASE) for p in pattern)
                    if matches:
                        if signal_name not in COMPONENTS["Vibration"]:
                            COMPONENTS["Vibration"].append(signal_name)
                            # logger.info(f"Signal '{signal_name}' added to Vibration")
                        matched = True
                        break  

                else:
                    if isinstance(pattern, str) and re.search(pattern, signal_name, re.IGNORECASE):
                        if signal_name not in COMPONENTS[component]:
                            COMPONENTS[component].append(signal_name)
                            # logger.info(f"Signal '{signal_name}' added to {component}")
                        matched = True
                        break 
                    
            if not matched:
                if signal_name not in COMPONENTS["Others"]:
                    COMPONENTS["Others"].append(signal_name)
                    # logger.info(f"Signal '{signal_name}' added to 'Others'")

        # logger.info(f"COMPONENTS updated: {COMPONENTS}")

    except Exception as e:
        logger.error(f"Error fetching data from MongoDB: {e}")

# Define the check_component function
def check_component(component_name, value):
    thresholds = THRESHOLDS.get(component_name, {})
    for status, check_fn in thresholds.items():
        if check_fn(value):
            return status
    return "unknown"

async def monitor(app):
    if collection is None:
        logger.error("MongoDB collection is not initialized.")
        return
    try:
        # Fetch all documents from MongoDB collection
        cursor = collection.find({})
        documents = await cursor.to_list(length = None)
        # logger.info(f"Total documents fetched {len(documents)}")
        # for document in documents:
        # documents = await asyncio.to_thread(list, cursor)
        for document in documents:
            l1_name = document.get("L1Name", "")
            signal_name = document.get("signalname", "")
            value = document.get("value", 0)
            update_date = document.get("updatedate", datetime.utcnow().replace(tzinfo=pytz.utc))
            
            if type(update_date) != datetime:
                continue
            else:
                # Ensure `update_date` is in UTC
                if update_date.tzinfo is None:
                    update_date = UTC.localize(update_date)
                ist_updatedate = convert_utc_to_ist(update_date)
            # else:
            #     ist_updatedate = None


            # Use a default value for missing `value`
            # if value is None:
            #     value = 0 
            # logger.info(f"Processing document: L1Name={l1_name}, SignalName={signal_name}, Value={value}, UpdateDate={update_date}")

            # Determine component name from signal name (this logic needs to match your specific use case)
            # component_name = next((comp for comp, signals in COMPONENTS.items() if signal_name in signals), None)
            component_name = None
            for comp in THRESHOLDS.keys():
                if signal_name in COMPONENTS.get(comp, []):
                    component_name = comp
                    break

            if component_name is None:
                continue

            status = check_component(component_name, value)

            table_name = f"{component_name}"
                       
            try:
                pool = await get_postgres_pool(app)
                async with pool.acquire() as conn:
                    # ist_updatedate = convert_utc_to_ist(update_date)
                    await conn.execute(f'''
                        INSERT INTO {table_name} (
                            l1name, signalname, updatedate, value, status,
                            ist_updatedate, insert_date
                        ) VALUES ($1, $2, $3::TIMESTAMP WITH TIME ZONE, $4::NUMERIC(10, 3), $5, $6::TIMESTAMP WITH TIME ZONE, CURRENT_DATE)
                        ON CONFLICT (l1name, signalname, updatedate) DO NOTHING;
                    ''', l1_name, signal_name, update_date, value, status, ist_updatedate)
                    
            except Exception as e:
                logger.error(f"Error inserting data into {table_name}: {e}")
                # logger.error(f"Exception: {e}")
            
        # logger.info("Threshold checking and PostgreSQL updates complete.")
        
    except Exception as e:
        logger.error(f"Error in monitor function: {e}")
   
async def active_monitor(app):
    
    try:
        pool = await get_postgres_pool(app)
        async with pool.acquire() as conn:
        # Remove outdated records
            await conn.execute('''
                DELETE FROM Active
                WHERE insert_date < CURRENT_DATE
            ''')
        cursor = collection.find({})
        documents = await cursor.to_list(length = None)

         # Get the current date in UTC
        current_utc_date = datetime.now(timezone.utc).date()
        
        for document in documents:
            l1_name = document.get("L1Name", "")
            signal_name = document.get("signalname", "")
            value = document.get("value", None)
            update_date = document.get("updatedate", None)

             # Skip documents that are missing either updatedate or value
            if not update_date or value is None:
                continue
            
             # Extract the date part from update_date
            update_date_only = update_date.date()

            # Only process documents where updatedate is today
            if update_date_only != current_utc_date:
                continue
            
            ist_updatedate = convert_utc_to_ist(update_date)

            component_name = None
            for comp, signals in COMPONENTS.items():
                if signal_name in signals:
                    component_name = comp
                    break

            if component_name is None:
                continue

            status = check_component(component_name, value)

            # Insert or update the record in PostgreSQL
            pool = await get_postgres_pool(app)
            async with pool.acquire() as conn:
                # ist_updatedate = convert_utc_to_ist(update_date)
                await conn.execute('''
                    INSERT INTO Active (l1name, signalname, updatedate, value, status, ist_updatedate, insert_date)
                    VALUES ($1, $2, $3::TIMESTAMP WITH TIME ZONE, $4::NUMERIC(10, 2), $5, $6::TIMESTAMP WITH TIME ZONE, CURRENT_DATE)
                    ON CONFLICT (l1name, signalname)
                    DO UPDATE SET 
                        value = EXCLUDED.value,
                        status = EXCLUDED.status,
                        updatedate = EXCLUDED.updatedate,        
                        ist_updatedate = EXCLUDED.ist_updatedate,
                        insert_date = CURRENT_DATE
                ''', l1_name, signal_name, update_date, value, status, ist_updatedate)

    except Exception as e:
        logger.error(f"Error in active_monitor function: {e}")

async def run_daily_task(app):
    while True:
        try:
            await active_monitor(app)
        except Exception as e:
            print(f"Error in daily task: {e}")
        
        # Calculate time until midnight and sleep until then
        # now = datetime.now()
        # tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        # delta = tomorrow - now
        # await asyncio.sleep(delta.total_seconds())


# Main monitoring task function 
async def background_monitoring_tasks(app):
    while True:
        
        try:
            await monitor(app),
            await active_monitor(app)
          
        except Exception as e:
            logger.info(f"Error in monitoring task: {e}")
        # await asyncio.sleep(5)
