import requests
import time
import sys
from requests.auth import HTTPBasicAuth
import json

# API credentials
API_USERNAME = "admin"
API_PASSWORD = "hospital2025"

# Base URL for the API
BASE_URL = "http://localhost:5000"

def test_connection():
    """Test the connection to the API."""
    try:
        response = requests.get(f"{BASE_URL}/", 
                               auth=HTTPBasicAuth(API_USERNAME, API_PASSWORD))
        
        if response.status_code == 200:
            print("✅ Connection to API successful")
            return True
        else:
            print(f"❌ API connection failed with status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure the containers are running.")
        return False

def test_get_patients():
    """Test retrieving all patients."""
    try:
        response = requests.get(f"{BASE_URL}/patients/", 
                               auth=HTTPBasicAuth(API_USERNAME, API_PASSWORD))
        
        if response.status_code == 200:
            patients = response.json()
            print(f"✅ Retrieved {len(patients)} patients")
            return True
        else:
            print(f"❌ Failed to retrieve patients. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error retrieving patients: {e}")
        return False

def test_create_patient():
    """Test creating a new patient."""
    new_patient = {
        "patient_name": "Test Patient",
        "date_of_birth": "2000-01-01",
        "admission_date": "2025-04-16",
        "diagnosis": "Test Diagnosis",
        "attending_physician": "Dr. Test",
        "room_number": "TEST",
        "discharge_status": False
    }
    
    try:
        response = requests.post(f"{BASE_URL}/patients/", 
                                json=new_patient,
                                auth=HTTPBasicAuth(API_USERNAME, API_PASSWORD))
        
        if response.status_code == 200:
            created_patient = response.json()
            print(f"✅ Created patient with ID: {created_patient['patient_id']}")
            return created_patient['patient_id']
        else:
            print(f"❌ Failed to create patient. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error creating patient: {e}")
        return None

def test_get_patient(patient_id):
    """Test retrieving a specific patient."""
    try:
        response = requests.get(f"{BASE_URL}/patients/{patient_id}", 
                               auth=HTTPBasicAuth(API_USERNAME, API_PASSWORD))
        
        if response.status_code == 200:
            patient = response.json()
            print(f"✅ Retrieved patient: {patient['patient_name']}")
            return True
        else:
            print(f"❌ Failed to retrieve patient. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error retrieving patient: {e}")
        return False

def test_update_patient(patient_id):
    """Test updating a patient."""
    updated_patient = {
        "patient_name": "Updated Test Patient",
        "date_of_birth": "2000-01-01",
        "admission_date": "2025-04-16",
        "diagnosis": "Updated Diagnosis",
        "attending_physician": "Dr. Updated",
        "room_number": "UPD",
        "discharge_status": True
    }
    
    try:
        response = requests.put(f"{BASE_URL}/patients/{patient_id}", 
                               json=updated_patient,
                               auth=HTTPBasicAuth(API_USERNAME, API_PASSWORD))
        
        if response.status_code == 200:
            updated = response.json()
            print(f"✅ Updated patient: {updated['patient_name']}")
            return True
        else:
            print(f"❌ Failed to update patient. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error updating patient: {e}")
        return False

def test_delete_patient(patient_id):
    """Test deleting a patient."""
    try:
        response = requests.delete(f"{BASE_URL}/patients/{patient_id}", 
                                  auth=HTTPBasicAuth(API_USERNAME, API_PASSWORD))
        
        if response.status_code == 200:
            print(f"✅ Deleted patient with ID: {patient_id}")
            return True
        else:
            print(f"❌ Failed to delete patient. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error deleting patient: {e}")
        return False

def main():
    print("🏥 Hospital System Verification Script 🏥")
    print("----------------------------------------")
    
    # Wait for services to start up
    print("Waiting for services to start up...")
    time.sleep(5)
    
    # Test connection to API
    if not test_connection():
        sys.exit(1)
    
    # Test getting all patients
    if not test_get_patients():
        sys.exit(1)
    
    # Test patient creation
    patient_id = test_create_patient()
    if patient_id is None:
        sys.exit(1)
    
    # Test getting a specific patient
    if not test_get_patient(patient_id):
        sys.exit(1)
    
    # Test updating a patient
    if not test_update_patient(patient_id):
        sys.exit(1)
    
    # Test deleting a patient
    if not test_delete_patient(patient_id):
        sys.exit(1)
    
    print("\n✨ All tests passed! You've completed the challenge! ✨")

if __name__ == "__main__":
    main()
