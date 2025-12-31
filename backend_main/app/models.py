from pydantic import BaseModel
from datetime import date

class MachineName(BaseModel):
    selected_machine_name:str

class SignalName(BaseModel):
    selected_signal_name:str

class MachineData(BaseModel):
    value: float
    ist_updatedate: date  