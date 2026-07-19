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


