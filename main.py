from fastapi import FastAPI, HTTPException
import json

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello, This is patient management system"}


def load_patients():
    with open("patients.json", "r") as file:
        return json.load(file);


@app.get("/patients")
def get_all():
    return load_patients()


@app.get("/patients/{patient_id}")
def get_by_id(patient_id : str):
    if patient_id in load_patients():
        return load_patients()[patient_id]
    else:
        raise HTTPException(status_code = 404, detail = "Patient not found")


@app.get("/sort")
def sort_all(sort_by : str, order : str = "asc"):
    patients = load_patients();
    type = ['name','age','height','weight','bmi'];
    if sort_by not in type:
        raise HTTPException(status_code = 400, detail = "Invalid sort type")
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code = 400, detail = "Invalid order type")
    sorted_patients = sorted(patients.items(), key = lambda x : x[1][sort_by], reverse = order=='desc')
    return sorted_patients;

@app.post("/patients")
