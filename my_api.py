from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI()

# Authentication setup
security = HTTPBasic()

# In-memory database for patient records
patients_db = {}

# Pydantic model for patient data
class Patient(BaseModel):
    id: int = Field(..., example=1)
    name: str = Field(..., example="John Doe")
    age: int = Field(..., ge=0, example=30)
    condition: str = Field(..., example="Hypertension")

# Dependency for authentication
def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != "admin" or credentials.password != "password":
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return credentials

# Endpoint to add a new patient
@app.post("/patients/", status_code=201, response_model=Patient)
def add_patient(patient: Patient, credentials: HTTPBasicCredentials = Depends(authenticate)):
    if patient.id in patients_db:
        raise HTTPException(status_code=400, detail="Patient with this ID already exists")
    patients_db[patient.id] = patient
    return patient

# Endpoint to retrieve all patients
@app.get("/patients/", response_model=List[Patient])
def get_patients(credentials: HTTPBasicCredentials = Depends(authenticate)):
    return list(patients_db.values())

# Endpoint to retrieve a specific patient by ID
@app.get("/patients/{patient_id}", response_model=Patient)
def get_patient(patient_id: int, credentials: HTTPBasicCredentials = Depends(authenticate)):
    patient = patients_db.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

# Endpoint to update a patient's record
@app.put("/patients/{patient_id}", response_model=Patient)
def update_patient(patient_id: int, updated_patient: Patient, credentials: HTTPBasicCredentials = Depends(authenticate)):
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")
    patients_db[patient_id] = updated_patient
    return updated_patient

# Endpoint to delete a patient
@app.delete("/patients/{patient_id}", status_code=204)
def delete_patient(patient_id: int, credentials: HTTPBasicCredentials = Depends(authenticate)):
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")
    del patients_db[patient_id]