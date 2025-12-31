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

# Define UTC and IST timezones
UTC = pytz.utc
IST = pytz.timezone('Asia/Kolkata')

def convert_utc_to_ist(utc_datetime):
    if utc_datetime.tzinfo is None:
        utc_datetime = pytz.utc.localize(utc_datetime)
    return utc_datetime.astimezone(IST)

THRESHOLD_TABLE_SCHEMA = '''
    CREATE TABLE IF NOT EXISTS Thresholds (
        id SERIAL PRIMARY KEY,
        l1name VARCHAR(255),
        signalname VARCHAR(255),
        component VARCHAR(50),
        low NUMERIC,
        normalmin NUMERIC,
        normalmax NUMERIC,
        high NUMERIC,
        UNIQUE (l1name, signalname)
'''

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
            # Create thresholds table first
            await conn.execute(THRESHOLD_TABLE_SCHEMA)
            logger.info("Thresholds table created successfully.")
            
            active_table_schema = table_schema_template.format(
                table_name='Active',
                unique_constraints='UNIQUE (l1name, signalname)'
            )    
            await conn.execute(active_table_schema)
            logger.info("Active table created successfully.")
            
            for table_name in COMPONENTS.keys():
                table_schema = table_schema_template.format(
                    table_name=table_name,
                    unique_constraints='UNIQUE (l1name, signalname, updatedate)'
                )
                await conn.execute(table_schema)
                logger.info(f"{table_name} table created successfully.")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")

async def machine_signal_append():
    try:
        cursor = collection.find({})
        documents = await cursor.to_list(length = None)
        logger.info(f"Total documents fetched from MongoDB: {len(documents)}")

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

                    matches = any(re.search(p, signal_name, re.IGNORECASE) for p in pattern)
                    if matches:
                        if signal_name not in COMPONENTS["Vibration"]:
                            COMPONENTS["Vibration"].append(signal_name)
                        matched = True
                        break  
                else:
                    if isinstance(pattern, str) and re.search(pattern, signal_name, re.IGNORECASE):
                        if signal_name not in COMPONENTS[component]:
                            COMPONENTS[component].append(signal_name)
                        matched = True
                        break 
                    
            if not matched:
                if signal_name not in COMPONENTS["Others"]:
                    COMPONENTS["Others"].append(signal_name)

    except Exception as e:
        logger.error(f"Error fetching data from MongoDB: {e}")

async def check_component(app, l1name, signalname, component_name, value):
    try:
        pool = await get_postgres_pool(app)
        async with pool.acquire() as conn:
            threshold = await conn.fetchrow(
                'SELECT low, normalmin, normalmax, high FROM Thresholds WHERE l1name = $1 AND signalname = $2',
                l1name, signalname
            )
            
            if not threshold:
                # Use default thresholds if specific ones aren't found
                threshold = await conn.fetchrow(
                    'SELECT low, normalmin, normalmax, high FROM Thresholds WHERE l1name = $1 AND component = $2',
                    'default', component_name
                )
                if not threshold:
                    return "unknown"

            low = threshold['low']
            normalmin = threshold['normalmin']
            normalmax = threshold['normalmax']
            high = threshold['high']

            if component_name == "Pressure":
                if value > high:
                    return "High"
                elif value >= normalmin:
                    return "Normal"
                else:
                    return "Normal"
            elif component_name == "Level":
                if value < high:
                    return "High"
                elif value >= normalmin:
                    return "Normal"
                else:
                    return "Normal"
            elif component_name == "Vibration":
                if 'Spin' in signalname:
                    if value > high:
                        return "Spn_High"
                    elif value >= normalmin:
                        return "Spn_Tolerance"
                    else:
                        return "Spn_Normal"
                else:  # Motor vibration
                    if value > high:
                        return "Mtr_High"
                    elif value >= normalmin:
                        return "Mtr_Tolerance"
                    else:
                        return "Mtr_Normal"
            elif component_name == "Temperature":
                if value > high:
                    return "High"
                elif value >= low:
                    return "Normal"
                else:
                    return "Low"
            elif component_name == "Energy":
                if value == 0:
                    return "Switched_Off"
                elif value > normalmax:
                    return "High"
                elif value > normalmin:
                    return "Normal"
                else:
                    return "Normal"
            else:
                return "unknown"
    except Exception as e:
        logger.error(f"Error checking component status: {e}")
        return "unknown"

async def monitor(app):
    if collection is None:
        logger.error("MongoDB collection is not initialized.")
        return
    try:
        cursor = collection.find({})
        documents = await cursor.to_list(length = None)
        
        for document in documents:
            l1_name = document.get("L1Name", "")
            signal_name = document.get("signalname", "")
            value = document.get("value", 0)
            update_date = document.get("updatedate", datetime.utcnow().replace(tzinfo=pytz.utc))
            
            if type(update_date) != datetime:
                continue
            else:
                if update_date.tzinfo is None:
                    update_date = UTC.localize(update_date)
                ist_updatedate = convert_utc_to_ist(update_date)

            component_name = None
            for comp in COMPONENTS.keys():
                if signal_name in COMPONENTS.get(comp, []):
                    component_name = comp
                    break

            if component_name is None:
                continue

            status = await check_component(app, l1_name, signal_name, component_name, value)
                       
            try:
                pool = await get_postgres_pool(app)
                async with pool.acquire() as conn:
                    await conn.execute(f'''
                        INSERT INTO {component_name} (
                            l1name, signalname, updatedate, value, status,
                            ist_updatedate, insert_date
                        ) VALUES ($1, $2, $3::TIMESTAMP WITH TIME ZONE, $4::NUMERIC(10, 3), $5, $6::TIMESTAMP WITH TIME ZONE, CURRENT_DATE)
                        ON CONFLICT (l1name, signalname, updatedate) DO NOTHING;
                    ''', l1_name, signal_name, update_date, value, status, ist_updatedate)
                    
            except Exception as e:
                logger.error(f"Error inserting data into {component_name}: {e}")
            
    except Exception as e:
        logger.error(f"Error in monitor function: {e}")
   
async def active_monitor(app):
    try:
        pool = await get_postgres_pool(app)
        async with pool.acquire() as conn:
            await conn.execute('''
                DELETE FROM Active
                WHERE insert_date < CURRENT_DATE
            ''')
        
        cursor = collection.find({})
        documents = await cursor.to_list(length = None)
        current_utc_date = datetime.now(timezone.utc).date()
        
        for document in documents:
            l1_name = document.get("L1Name", "")
            signal_name = document.get("signalname", "")
            value = document.get("value", None)
            update_date = document.get("updatedate", None)

            if not update_date or value is None:
                continue
            
            update_date_only = update_date.date()
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

            status = await check_component(app, l1_name, signal_name, component_name, value)

            pool = await get_postgres_pool(app)
            async with pool.acquire() as conn:
                result = await conn.execute('''
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

                if value is not None:
                    logger.info(f"✅ Active updated: {l1_name} | {signal_name} | Value: {value} | Status: {status}")

    except Exception as e:
        logger.error(f"Error in active_monitor function: {e}")

async def run_daily_task(app):
    while True:
        try:
            await active_monitor(app)
        except Exception as e:
            print(f"Error in daily task: {e}")
        await asyncio.sleep(60)  # Check every minute

async def background_monitoring_tasks(app):
    while True:
        try:
            await monitor(app)
            await active_monitor(app)
        except Exception as e:
            logger.info(f"Error in monitoring task: {e}")
        await asyncio.sleep(5)


#         CREATE TABLE thresholds (
#     id SERIAL PRIMARY KEY,
#     l1name VARCHAR(255),
#     signalname VARCHAR(255),
#     component VARCHAR(50),
#     low NUMERIC,
#     normalmin NUMERIC,
#     normalmax NUMERIC,
#     high NUMERIC
# );
