from fastapi import FastAPI,HTTPException
import h5py
from pydantic import BaseModel
from typing import Dict, List
import psycopg2
import logging
import datetime
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

# Initialize FastAPI
app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enable CORS for all origins (for development purposes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# PostgreSQL connection settings
DB_HOST = "localhost"
DB_NAME = "vb_data"
DB_USER = "postgres"
DB_PASSWORD = "1234" 
DB_PORT = "5432"
conn = psycopg2.connect(
    dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
)
cursor = conn.cursor()


# Pydantic models for data structure
class VibrationData(BaseModel):
    machine_id: str
    # machine_name: str
    meas_point: str
    date: str
    time: str
    vibration_value: float
    frequency: float  
    base: str = None
    remarks:str
class PathValuesResponse(BaseModel):
    paths: List[VibrationData]
class MachineIDResponse(BaseModel):
    machine_ids: List[str]

class MeasPointResponse(BaseModel):
    meas_points: List[str]

class DateResponse(BaseModel):
    dates: List[str]

class TimeResponse(BaseModel):
    times: List[str]

class VibrationValuesResponse(BaseModel):
    vibration_values: List[VibrationData]
class DataModel(BaseModel):
    machine_id: str
    meas_point: str
    bd: float  # Ball Diameter
    pd: float  # Pitch Circle Diameter
    noofballs: int  # Number of Balls
    angle:int
    rpm:float
    other:str
class HDF5Path(BaseModel):
    path: str

class DefectResponse(BaseModel):
    outer_race: float
    inner_race: float
    ball_defect: float
    cage_defect:float
class rpm(BaseModel):
    rpm:float
    other:str
# Function to get all machine IDs using SQL query
def get_all_machine_ids():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()

        query = "SELECT DISTINCT machine_id FROM data;"
        cursor.execute(query)
        rows = cursor.fetchall()

        machine_ids = [row[0] for row in rows]

        cursor.close()
        conn.close()

        return machine_ids
    except Exception as e:
        print(f"Error fetching machine IDs: {e}")
        return []


# Function to get measurement points for a given machine ID using SQL query
def get_meas_points_for_machine(machine_id: str):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()

        query = "SELECT DISTINCT meas_point FROM data WHERE machine_id = %s;"
        cursor.execute(query, (machine_id,))
        rows = cursor.fetchall()

        meas_points = [row[0] for row in rows]

        cursor.close()
        conn.close()

        return meas_points
    except Exception as e:
        print(f"Error fetching measurement points: {e}")
        return []



def get_dates_for_machine_and_meas_point(machine_id: str, meas_point: str):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()

        query = """
            SELECT DISTINCT date 
            FROM data 
            WHERE machine_id = %s AND meas_point = %s 
            ORDER BY date;
        """
        cursor.execute(query, (machine_id, meas_point))
        rows = cursor.fetchall()

        dates = [row[0].strftime('%Y-%m-%d') for row in rows]

        cursor.close()
        conn.close()

        return dates
    except Exception as e:
        print(f"Error fetching dates: {e}")
        return []



# Function to get times and remarks for a given machine ID, measurement point, and date using SQL query
def get_times_for_machine_and_meas_point_and_date(machine_id: str, meas_point: str, date: datetime.date):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()

        query = """
            SELECT time, remarks 
            FROM data 
            WHERE machine_id = %s AND meas_point = %s AND date = %s
            ORDER BY time;
        """
        cursor.execute(query, (machine_id, meas_point, date))
        rows = cursor.fetchall()

        # Extract unique times (ignore duplicates)
        unique_times = set()
        times_with_remarks = []
        
        for row in rows:
            time_str = row[0].strftime('%H:%M:%S')
            if time_str not in unique_times:
                unique_times.add(time_str)
                # Combine time and remarks in the required format
                times_with_remarks.append(f"{time_str} {row[1]}" if row[1] else f"{time_str}")

        cursor.close()
        conn.close()

        return times_with_remarks
    except Exception as e:
        print(f"Error fetching times and remarks: {e}")
        return []



# Function to get vibration values using SQL query
def get_vibration_values(machine_id: str, meas_point: str, date: datetime.date, time: datetime.time):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()

        # Query to fetch data
        query = """
            SELECT machine_id, meas_point, date, time, vibration_value, frequency, base 
            FROM data 
            WHERE machine_id = %s 
              AND meas_point = %s 
              AND date = %s
              AND time::time = %s::time;
        """

        print(f"Executing query with machine_id={machine_id}, meas_point={meas_point}, date={date}, time={time}")

        cursor.execute(query, (machine_id, meas_point, date, time))
        rows = cursor.fetchall()

        vibration_values = []
        
        for row in rows:
            try:
                # Handle remarks separately since it's not in the query result
                remarks = "N/A"  # Default value for remarks

                vibration_values.append(
                    VibrationData(
                        machine_id=row[0],
                        meas_point=row[1],
                        date=row[2].strftime('%Y-%m-%d'),
                        time=row[3].strftime('%H:%M:%S'),
                        vibration_value=float(row[4]) if row[4] is not None else 0.0,  # Default to 0.0 if None
                        frequency=float(row[5]) if row[5] is not None else 0.0,  # Default to 0.0 if None
                        base=row[6] if row[6] else "N/A",  # Handle possible None values
                        remarks=remarks  # Default remarks value
                    )
                )
            except Exception as e:
                print(f"Error processing row {row}: {e}")

        cursor.close()
        conn.close()

        return vibration_values
    except Exception as e:
        print(f"Error fetching vibration values: {e}")
        return []
@app.get("/vibration_values/{machine_id}/{meas_point}/{date}/{time}/", response_model=VibrationValuesResponse)
def get_vibration_data(machine_id: str, meas_point: str, date: str, time: str):
    # Print incoming parameters for debugging
    print(f"Received parameters: machine_id={machine_id}, meas_point={meas_point}, date={date}, time={time}")
    
    # Clean the time string to remove any unexpected characters
    cleaned_time = time.split(" ")[0]  # This takes only the part before the space

    try:
        # Convert date and cleaned time strings to datetime objects
        date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        time_obj = datetime.datetime.strptime(cleaned_time, '%H:%M:%S').time()

        vibration_values = get_vibration_values(machine_id, meas_point, date_obj, time_obj)

        return {"vibration_values": vibration_values}
    except Exception as e:
        print(f"Error in /vibration_values endpoint: {e}")
        return {"vibration_values": []}
def get_paths(machine_id: str, meas_point: str, date: datetime.date, time: datetime.time):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()

        # Query to fetch data
        query = """
            SELECT machine_id, meas_point, date, time, path, frequency, base 
            FROM data 
            WHERE machine_id = %s 
              AND meas_point = %s 
              AND date = %s
              AND time::time = %s::time;
        """

        print(f"Executing query with machine_id={machine_id}, meas_point={meas_point}, date={date}, time={time}")

        cursor.execute(query, (machine_id, meas_point, date, time))
        rows = cursor.fetchall()

        paths = []
        
        for row in rows:
            try:
                # Handle remarks separately since it's not in the query result
                remarks = "N/A"  # Default value for remarks

                paths.append(
                    VibrationData(
                        machine_id=row[0],
                        meas_point=row[1],
                        date=row[2].strftime('%Y-%m-%d'),
                        time=row[3].strftime('%H:%M:%S'),
                        path=float(row[4]) if row[4] is not None else 0.0,  # Default to 0.0 if None
                        frequency=float(row[5]) if row[5] is not None else 0.0,  # Default to 0.0 if None
                        base=row[6] if row[6] else "N/A",  # Handle possible None values
                        remarks=remarks  # Default remarks value
                    )
                )
            except Exception as e:
                print(f"Error processing row {row}: {e}")

        cursor.close()
        conn.close()

        return paths
    except Exception as e:
        print(f"Error fetching vibration values: {e}")
        return []
@app.get("/paths/{machine_id}/{meas_point}/{date}/{time}/", response_model=VibrationValuesResponse)
def get_vibration_data(machine_id: str, meas_point: str, date: str, time: str):
    # Print incoming parameters for debugging
    print(f"Received parameters: machine_id={machine_id}, meas_point={meas_point}, date={date}, time={time}")
    
    # Clean the time string to remove any unexpected characters
    cleaned_time = time.split(" ")[0]  # This takes only the part before the space

    try:
        # Convert date and cleaned time strings to datetime objects
        date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        time_obj = datetime.datetime.strptime(cleaned_time, '%H:%M:%S').time()

        paths = get_paths(machine_id, meas_point, date_obj, time_obj)

        return {"paths": paths}
    except Exception as e:
        print(f"Error in /paths endpoint: {e}")
        return {"paths": []}
def get_vibration_paths(machine_id: str, meas_point: str, date: datetime.date, time: datetime.time):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()

        query = """
            SELECT machine_id, meas_point, date, time, path, base 
            FROM data 
            WHERE machine_id = %s 
              AND meas_point = %s 
              AND date = %s
              AND time::time = %s::time;
        """

        print(f"Executing query with machine_id={machine_id}, meas_point={meas_point}, date={date}, time={time}")

        cursor.execute(query, (machine_id, meas_point, date, time))
        rows = cursor.fetchall()

        paths = []

        for row in rows:
            try:
                remarks = "N/A"  # Default value for remarks
                paths.append(
                    {
                        "machine_id": row[0],
                        "meas_point": row[1],
                        "date": row[2].strftime('%Y-%m-%d'),
                        "time": row[3].strftime('%H:%M:%S'),
                        "path": row[4] if row[4] else "N/A",
                       
                    }
                )
            except Exception as e:
                print(f"Error processing row {row}: {e}")

        cursor.close()
        conn.close()

        return paths
    except Exception as e:
        print(f"Error fetching paths: {e}")
        return []
@app.get("/vibration_paths/{machine_id}/{meas_point}/{date}/{time}/")
def get_path_data(machine_id: str, meas_point: str, date: str, time: str):
    print(f"Received parameters: machine_id={machine_id}, meas_point={meas_point}, date={date}, time={time}")
    cleaned_time = time.split(" ")[0]

    try:
        date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        time_obj = datetime.datetime.strptime(cleaned_time, '%H:%M:%S').time()

        path_data = get_vibration_paths(machine_id, meas_point, date_obj, time_obj)

        return {"paths": path_data}
    except Exception as e:
        print(f"Error in /vibration_paths endpoint: {e}")
        return {"paths": []}

def get_defect_frequencies(machine_id: str, meas_point: str):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()

        query = """
        SELECT outer_race, inner_race, ball_defect,cage_defect
        FROM collect
        WHERE machine_id = %s AND meas_point = %s;
        """
        cursor.execute(query, (machine_id, meas_point))
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if row:
            return {"outer_race": row[0], "inner_race": row[1], "ball_defect": row[2], "cage_defect":row[3]}
        else:
            return None
    except Exception as e:
        print(f"Error fetching defect frequencies: {e}")
        return None

@app.post("/read-hdf5")
def read_hdf5_data(hdf5: HDF5Path):
    try:
        with h5py.File(hdf5.path, 'r') as f:
            data = f['time_domain_data'][:]
            time = data[:, 0]
            vibration = data[:, 1]

        return {"x": time.tolist(), "y": vibration.tolist()}
    except Exception as e:
        print("Error reading HDF5:", e)
        return {"x": [], "y": []}



# API endpoint to get all machine IDs
@app.get("/machine_ids/", response_model=MachineIDResponse)
def get_machine_ids():
    machine_ids = get_all_machine_ids()
    return {"machine_ids": machine_ids}


# API endpoint to get measurement points for a given machine ID
@app.get("/meas_points/{machine_id}/", response_model=MeasPointResponse)
def get_meas_points(machine_id: str):
    meas_points = get_meas_points_for_machine(machine_id)
    return {"meas_points": meas_points}


# API endpoint to get dates for a given machine ID and measurement point
@app.get("/dates/{machine_id}/{meas_point}/", response_model=DateResponse)
def get_dates(machine_id: str, meas_point: str):
    dates = get_dates_for_machine_and_meas_point(machine_id, meas_point)
    return {"dates": dates}


# API endpoint to get times for a given machine ID, measurement point, and date
@app.get("/times/{machine_id}/{meas_point}/{date}/", response_model=TimeResponse)
def get_times(machine_id: str, meas_point: str, date: str):
    # Convert date string to datetime object
    date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    times = get_times_for_machine_and_meas_point_and_date(machine_id, meas_point, date_obj)
    return {"times": times}


# API endpoint to get vibration values for a given machine ID, measurement point, date, and time


# API endpoint to get the most recent BASE vibration values for a given machine ID and measurement point (without date and time)
# API endpoint to get all BASE vibration values for the most recent date for a given machine ID and measurement point
@app.get("/vibration_values/base/{machine_id}/{meas_point}/", response_model=VibrationValuesResponse)
def get_recent_base_vibration_data_for_date(machine_id: str, meas_point: str):
    try:
        # Step 1: Fetch the most recent date for the given machine_id and meas_point where base = 'BASE'
        with psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        ) as conn:
            with conn.cursor() as cursor:
                # Query to get the most recent date for the given machine_id and meas_point with base = 'BASE'
                query = """
                    SELECT DISTINCT date
                    FROM data 
                    WHERE machine_id = %s AND meas_point = %s AND base = 'BASE'
                    ORDER BY date DESC
                    LIMIT 1;
                """
                cursor.execute(query, (machine_id, meas_point))
                row = cursor.fetchone()

                if row is None:
                    return {"vibration_values": []}

                # The most recent date for base = 'BASE'
                recent_date = row[0]

                # Step 2: Fetch all vibration data for the most recent date where base = 'BASE'
                query = """
                    SELECT machine_id,meas_point, date, time, vibration_value, frequency, base 
                    FROM data 
                    WHERE machine_id = %s AND meas_point = %s AND base = 'BASE' AND date = %s
                    ORDER BY time DESC;
                """
                cursor.execute(query, (machine_id, meas_point, recent_date))
                rows = cursor.fetchall()

                vibration_values = []
                for row in rows:
                    vibration_values.append(
                        VibrationData(
                            machine_id=row[0],
                            # machine_name=row[1] if row[1] else "Unknown",
                            meas_point=row[1],
                            date=row[2].strftime('%Y-%m-%d'),
                            time=row[3].strftime('%H:%M:%S'),
                            vibration_value=float(row[4]) if row[4] is not None else 0.0,
                            frequency=float(row[5]) if row[5] is not None else 0.0,
                            base=row[6] if row[6] else "N/A",
                            remarks="N/A"  # Default remarks value
                        )
                    )

        return {"vibration_values": vibration_values}
        
    except Exception as e:
        print(f"Error in /vibration_values/base endpoint: {e}")
        raise HTTPException(status_code=500, detail="Error fetching vibration values")

@app.post("/save")
def save_data(data: DataModel):
    print("Ptiny", data)
    try:
        cursor.execute(
            "INSERT INTO collect (machine_id, meas_point, bd, pd, noofballs,angle,rpm,other) VALUES (%s, %s, %s, %s, %s,%s,%s,%s)",
            (data.machine_id, data.meas_point, data.bd, data.pd, data.noofballs,data.angle,data.rpm,data.other),
        )
        conn.commit()
        return {"message": "Data saved successfully!"}
    except Exception as e:
        return {"error": str(e)}
@app.get("/machine-idds", response_model=List[str])
def get_all_machine_ids():
    cursor.execute("SELECT DISTINCT machine_id FROM collect")
    machine_ids = [row[0] for row in cursor.fetchall()]
    return machine_ids

# 2. Fetch all machine_id and their corresponding machine_name
@app.get("/machine-name/{machine_id}", response_model=str)
def get_machine_name_by_id(machine_id: str):
    cursor.execute("SELECT machine_name FROM collect WHERE machine_id = %s LIMIT 1", (machine_id,))
    row = cursor.fetchone()
    if row:
        return row[0]
    return "Machine name not found"


# 3. Fetch all measurement points for a given machine_id
@app.get("/measurement-points/{machine_id}", response_model=List[str])
def get_measurement_points(machine_id: str):
    cursor.execute("SELECT DISTINCT meas_point FROM collect WHERE machine_id = %s", (machine_id,))
    points = [row[0] for row in cursor.fetchall()]
    return points

# 4. Fetch all measurement names for a given measurement point
@app.get("/measurement-names/{meas_point}", response_model=List[str])
def get_measurement_names(meas_point: str):
    cursor.execute("SELECT DISTINCT meas_name FROM collect WHERE meas_point = %s LIMIT 1", (meas_point,))
    name = [row[0] for row in cursor.fetchall()]
    return name
# API endpoint to fetch all details (machine_id and meas_point) from the 'create' table
@app.get("/get_all")
def get_all_data():
    try:
        cursor.execute("SELECT * FROM collect")
        data = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]  # Get column names
        result = [dict(zip(columns, row)) for row in data]  # Convert to list of dictionaries
        return {"data": result, "message": "Data retrieved successfully!"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/vbcollect/all")
async def get_all_vbcollect_data():
    try:
        cursor.execute("Select machine_id,meas_point,band1,band2,band3,band4,overall_rms,remarks,date FROM vibration_output")
        result = cursor.fetchall()
        return {"data": result}
    except Exception as e:
        print(f"Error fetching data from 'vibration_output' table: {e}")
        raise HTTPException(status_code=500, detail="Error fetching data from 'vibration_output' table")
@app.delete("/vbcollect/delete/{machine_id}/{meas_point}/{band1},{band2},{band3},{band4},{overall_rms},{remarks},{date}")
def delete_vbcollect_record(machine_id: str, meas_point: str, band1: float, band2: float, band3: float, band4: float, overall_rms: float, remarks: str, date: str):
    try:
        cursor.execute("DELETE FROM vibration_output WHERE machine_id = %s AND meas_point = %s AND band1 = %s AND band2 = %s AND band3 = %s AND band4 = %s AND overall_rms = %s AND remarks = %s AND date = %s", (machine_id, meas_point, band1, band2, band3, band4, overall_rms, remarks, date))
        conn.commit()
        
        # Check if any row was deleted
        if cursor.rowcount > 0:
            return {"message": "Record deleted successfully"}
        else:
            return {"message": "No record found to delete"}
    except Exception as e:
        print(f"Error deleting record from 'vibration_output' table: {e}")
        raise HTTPException(status_code=500, detail="Error deleting record from 'vibration_output' table")
# API endpoint to delete a record from the 'create' table
@app.delete("/delete/{machine_id}/{meas_point}")
def delete_collect_record(machine_id: str, meas_point: str):
    try:
        cursor.execute("DELETE FROM collect WHERE machine_id = %s AND meas_point = %s", (machine_id, meas_point))
        conn.commit()
        
        if cursor.rowcount > 0:
            return {"message": "Record deleted successfully"}
        else:
            return {"message": "No record found to delete"}
    except Exception as e:
        print(f"Error deleting record from 'collect' table: {e}")
        raise HTTPException(status_code=500, detail="Error deleting record from 'collect' table")
@app.get("/defect_frequencies/{machine_id}/{meas_point}/", response_model=DefectResponse)
def get_defect_frequencies_api(machine_id: str, meas_point: str):
    defect_data = get_defect_frequencies(machine_id, meas_point)
    if defect_data:
        return defect_data
    else:
        raise HTTPException(status_code=404, detail="Defect data not found")
def get_RPM(machine_id: str, meas_point: str):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()

        query = """
        SELECT rpm, other
        FROM collect
        WHERE machine_id = %s AND meas_point = %s;
        """
        cursor.execute(query, (machine_id, meas_point))
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if row:
            return {"rpm": row[0], "other": row[1]}
        else:
            return None
    except Exception as e:
        print(f"error: {e}")
        return None

@app.get("/rpm/{machine_id}/{meas_point}/", response_model=rpm)
def get_rpm_api(machine_id: str, meas_point: str):
    rpm_data = get_RPM(machine_id, meas_point)
    if rpm_data:
        return rpm_data
    else:
        raise HTTPException(status_code=404, detail="Defect data not found")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)
