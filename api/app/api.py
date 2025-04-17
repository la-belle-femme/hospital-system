from fastapi import FastAPI, Depends, HTTPException, status, Request, Form, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import psycopg2
import os
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel
import secrets

app = FastAPI(title="Hospital Patient Management System")
security = HTTPBasic()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="templates")

# Database connection parameters
DB_HOST = os.environ.get("DB_HOST", "database")
DB_NAME = os.environ.get("DB_NAME", "hospital_db")
DB_USER = os.environ.get("DB_USER", "hospital_admin")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "secure_password")

# Define data models
class Patient(BaseModel):
    patient_id: Optional[int] = None
    patient_name: str
    date_of_birth: date
    admission_date: date
    diagnosis: Optional[str] = None
    attending_physician: Optional[str] = None
    room_number: Optional[str] = None
    discharge_status: bool = False

# Basic authentication
def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "hospital2025")
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Web authentication - simplified for the demo
async def web_auth(request: Request):
    if "authorized" in request.cookies:
        return True
    return False

# Database connection function
def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

# API Routes
@app.get("/")
def read_root():
    return {"message": "Hospital Patient Management System API"}

@app.get("/patients/", response_model=List[Patient])
def read_patients(username: str = Depends(verify_credentials)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients")
    rows = cursor.fetchall()
    
    patients = []
    for row in rows:
        patient = Patient(
            patient_id=row[0],
            patient_name=row[1],
            date_of_birth=row[2],
            admission_date=row[3],
            diagnosis=row[4],
            attending_physician=row[5],
            room_number=row[6],
            discharge_status=row[7]
        )
        patients.append(patient)
    
    cursor.close()
    conn.close()
    return patients

@app.get("/patients/{patient_id}", response_model=Patient)
def read_patient(patient_id: int, username: str = Depends(verify_credentials)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE patient_id = %s", (patient_id,))
    row = cursor.fetchone()
    
    if row is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    patient = Patient(
        patient_id=row[0],
        patient_name=row[1],
        date_of_birth=row[2],
        admission_date=row[3],
        diagnosis=row[4],
        attending_physician=row[5],
        room_number=row[6],
        discharge_status=row[7]
    )
    
    cursor.close()
    conn.close()
    return patient

@app.post("/patients/", response_model=Patient)
def create_patient(patient: Patient, username: str = Depends(verify_credentials)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    INSERT INTO patients (patient_name, date_of_birth, admission_date, diagnosis, attending_physician, room_number, discharge_status)
    VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING patient_id
    """
    values = (
        patient.patient_name,
        patient.date_of_birth,
        patient.admission_date,
        patient.diagnosis,
        patient.attending_physician,
        patient.room_number,
        patient.discharge_status
    )
    
    cursor.execute(query, values)
    patient_id = cursor.fetchone()[0]
    conn.commit()
    
    cursor.close()
    conn.close()
    
    patient.patient_id = patient_id
    return patient

@app.put("/patients/{patient_id}", response_model=Patient)
def update_patient(patient_id: int, patient: Patient, username: str = Depends(verify_credentials)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if patient exists
    cursor.execute("SELECT * FROM patients WHERE patient_id = %s", (patient_id,))
    if cursor.fetchone() is None:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Update patient
    query = """
    UPDATE patients
    SET patient_name = %s, date_of_birth = %s, admission_date = %s, 
        diagnosis = %s, attending_physician = %s, room_number = %s, discharge_status = %s
    WHERE patient_id = %s
    """
    values = (
        patient.patient_name,
        patient.date_of_birth,
        patient.admission_date,
        patient.diagnosis,
        patient.attending_physician,
        patient.room_number,
        patient.discharge_status,
        patient_id
    )
    
    cursor.execute(query, values)
    conn.commit()
    
    cursor.close()
    conn.close()
    
    patient.patient_id = patient_id
    return patient

@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: int, username: str = Depends(verify_credentials)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if patient exists
    cursor.execute("SELECT * FROM patients WHERE patient_id = %s", (patient_id,))
    if cursor.fetchone() is None:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Delete patient
    cursor.execute("DELETE FROM patients WHERE patient_id = %s", (patient_id,))
    conn.commit()
    
    cursor.close()
    conn.close()
    
    return {"message": f"Patient with ID {patient_id} deleted successfully"}

# Web Interface Routes
@app.get("/web", response_class=HTMLResponse)
def web_home(request: Request):
    # For simplicity, we're setting a cookie to authenticate
    response = templates.TemplateResponse("index.html", {"request": request})
    response.set_cookie(key="authorized", value="true", httponly=True)
    return response

@app.get("/web/login", response_class=HTMLResponse)
def web_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/web/patients", response_class=HTMLResponse)
async def web_patients(request: Request, authorized: bool = Depends(web_auth)):
    if not authorized:
        return RedirectResponse(url="/web/login")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients")
    rows = cursor.fetchall()
    
    patients = []
    for row in rows:
        patient = {
            "patient_id": row[0],
            "patient_name": row[1],
            "date_of_birth": row[2],
            "admission_date": row[3],
            "diagnosis": row[4],
            "attending_physician": row[5],
            "room_number": row[6],
            "discharge_status": row[7]
        }
        patients.append(patient)
    
    cursor.close()
    conn.close()
    
    return templates.TemplateResponse("patients.html", {
        "request": request,
        "patients": patients
    })

@app.get("/web/patients/new", response_class=HTMLResponse)
async def web_new_patient_form(request: Request, authorized: bool = Depends(web_auth)):
    if not authorized:
        return RedirectResponse(url="/web/login")
    
    return templates.TemplateResponse("patient_form.html", {
        "request": request,
        "patient": {}
    })

@app.post("/web/patients/new", response_class=HTMLResponse)
async def web_create_patient(
    request: Request,
    patient_name: str = Form(...),
    date_of_birth: str = Form(...),
    admission_date: str = Form(...),
    diagnosis: Optional[str] = Form(None),
    attending_physician: Optional[str] = Form(None),
    room_number: Optional[str] = Form(None),
    discharge_status: Optional[bool] = Form(False),
    authorized: bool = Depends(web_auth)
):
    if not authorized:
        return RedirectResponse(url="/web/login")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    INSERT INTO patients (patient_name, date_of_birth, admission_date, diagnosis, attending_physician, room_number, discharge_status)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        patient_name,
        date_of_birth,
        admission_date,
        diagnosis,
        attending_physician,
        room_number,
        True if discharge_status else False
    )
    
    cursor.execute(query, values)
    conn.commit()
    
    cursor.close()
    conn.close()
    
    return RedirectResponse(url="/web/patients", status_code=303)

@app.get("/web/patients/{patient_id}", response_class=HTMLResponse)
async def web_patient_detail(patient_id: int, request: Request, authorized: bool = Depends(web_auth)):
    if not authorized:
        return RedirectResponse(url="/web/login")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE patient_id = %s", (patient_id,))
    row = cursor.fetchone()
    
    if row is None:
        cursor.close()
        conn.close()
        return RedirectResponse(url="/web/patients")
    
    patient = {
        "patient_id": row[0],
        "patient_name": row[1],
        "date_of_birth": row[2],
        "admission_date": row[3],
        "diagnosis": row[4],
        "attending_physician": row[5],
        "room_number": row[6],
        "discharge_status": row[7]
    }
    
    cursor.close()
    conn.close()
    
    return templates.TemplateResponse("patient_detail.html", {
        "request": request,
        "patient": patient
    })

@app.get("/web/patients/{patient_id}/edit", response_class=HTMLResponse)
async def web_edit_patient_form(patient_id: int, request: Request, authorized: bool = Depends(web_auth)):
    if not authorized:
        return RedirectResponse(url="/web/login")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE patient_id = %s", (patient_id,))
    row = cursor.fetchone()
    
    if row is None:
        cursor.close()
        conn.close()
        return RedirectResponse(url="/web/patients")
    
    patient = {
        "patient_id": row[0],
        "patient_name": row[1],
        "date_of_birth": row[2],
        "admission_date": row[3],
        "diagnosis": row[4],
        "attending_physician": row[5],
        "room_number": row[6],
        "discharge_status": row[7]
    }
    
    cursor.close()
    conn.close()
    
    return templates.TemplateResponse("patient_form.html", {
        "request": request,
        "patient": patient
    })

@app.post("/web/patients/{patient_id}/edit", response_class=HTMLResponse)
async def web_update_patient(
    patient_id: int,
    request: Request,
    patient_name: str = Form(...),
    date_of_birth: str = Form(...),
    admission_date: str = Form(...),
    diagnosis: Optional[str] = Form(None),
    attending_physician: Optional[str] = Form(None),
    room_number: Optional[str] = Form(None),
    discharge_status: Optional[bool] = Form(False),
    authorized: bool = Depends(web_auth)
):
    if not authorized:
        return RedirectResponse(url="/web/login")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if patient exists
    cursor.execute("SELECT * FROM patients WHERE patient_id = %s", (patient_id,))
    if cursor.fetchone() is None:
        cursor.close()
        conn.close()
        return RedirectResponse(url="/web/patients")
    
    # Update patient
    query = """
    UPDATE patients
    SET patient_name = %s, date_of_birth = %s, admission_date = %s, 
        diagnosis = %s, attending_physician = %s, room_number = %s, discharge_status = %s
    WHERE patient_id = %s
    """
    values = (
        patient_name,
        date_of_birth,
        admission_date,
        diagnosis,
        attending_physician,
        room_number,
        True if discharge_status else False,
        patient_id
    )
    
    cursor.execute(query, values)
    conn.commit()
    
    cursor.close()
    conn.close()
    
    return RedirectResponse(url="/web/patients", status_code=303)

@app.post("/web/patients/{patient_id}/delete", response_class=HTMLResponse)
async def web_delete_patient(patient_id: int, request: Request, authorized: bool = Depends(web_auth)):
    if not authorized:
        return RedirectResponse(url="/web/login")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if patient exists
    cursor.execute("SELECT * FROM patients WHERE patient_id = %s", (patient_id,))
    if cursor.fetchone() is None:
        cursor.close()
        conn.close()
        return RedirectResponse(url="/web/patients")
    
    # Delete patient
    cursor.execute("DELETE FROM patients WHERE patient_id = %s", (patient_id,))
    conn.commit()
    
    cursor.close()
    conn.close()
    
    return RedirectResponse(url="/web/patients", status_code=303)
