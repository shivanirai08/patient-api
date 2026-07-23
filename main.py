from fastapi import FastAPI, HTTPException
import json
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
from ml_model import predict
from fastapi.responses import JSONResponse

app = FastAPI()

class Patient(BaseModel):
    id : Annotated[str, Field(..., description = "The ID of the patient")]
    name : Annotated[str, Field(..., description = "Name of the patient")]
    city : Annotated[str, Field(..., description = "City of the patient")]
    age : Annotated[int, Field(..., description = "Age of the patient", gt = 0, lt = 120)]
    gender : Annotated[Literal["male", "female", "others"], Feild(..., description = "Gender of the patient")]
    height : Annotated[float, Field(..., description = "Height of the patient in cm", gt = 0, lt = 250)]
    weight : Annotated[float, Field(..., description = "Weight of the patient in kg", gt = 0, lt = 300)]

    @computed_field
    @property
    def bmi(self) -> float : 

        return round(self.weight / ((self.height/100) ** 2),2);

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi <18.5 :
            return "Underweight"
        if self.bmi < 25 :
            return "Normal"
        if self.bmi < 30 :
            return "Overweight"
        else :
            return "Obese"

class PatientUpdate(BaseModel) :
    name : Optional[str] = Field(default = None, description = "Name of the patient")
    city : Optional[str] = Field(default = None, description = "City of the patient")
    age : Optional[int] = Field(default = None, description = "Age of the patient", gt = 0, lt = 120)
    gender : Optional[Literal["male", "female", "others"]] = Field(default = None, description = "Gender of the patient")
    height : Optional[float] = Field(default = None, description = "Height of the patient in cm", gt = 0, lt = 250)
    weight : Optional[float] = Field(default = None, description = "Weight of the patient in kg", gt = 0, lt = 300)

class IrisRequest(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

@app.get("/")
def home():
    return {"message": "Hello, This is patient management system"}


def load_patients():
    with open("patients.json", "r") as file:
        return json.load(file)

def save_data(data):
    with open("patients.json", "w") as file:
        json.dump(data, file)


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
def create_patients(patient : Patient) :

    data = load_patients()

    if patient.id in data:
        raise HTTPException(status_code = 400, detail = "Patient already exists")

    data[patient.id] = patient.model_dump()

    save_data(data)
    
    return JSONResponse(status_code = 201, content = {"message": "Patient created successfully"})


@app.put("/patients/{patient_id}")
def update_patient(patient_id : str, patient : PatientUpdate) :
    data = load_patients()

    if patient_id not in data:
        raise HTTPException(status_code = 404, detail = "Patient not found") 

    updated_patient = patient.model_dump(exclude_unset = True)
    
    existing_patient = data[patient_id]
    existing_patient.update(updated_patient)
    
    existing_patient["id"] = patient_id
    patient_py_obj = Patient(**existing_patient)

    data[patient_id] = patient_py_obj.model_dump()

    save_data(data)

    return JSONResponse(status_code = 200, content = {"message": "Patient updated successfully"})


@app.delete("/patients/{patient_id}")
def delete_patient(patient_id : str) :
    data = load_patients()
    if patient_id not in data:
        raise HTTPException(status_code = 404, detail = "Patient not found")
    del data[patient_id]
    save_data(data)
    return JSONResponse(status_code = 200, content = {"message": "Patient deleted successfully"})




@app.post("/predict")
def predict_data(data : IrisRequest) :
    features = [data.sepal_length, data.sepal_width, data.petal_length, data.petal_width]
    prediction = predict(features)
    return JSONResponse(status_code = 200, content = {"prediction": prediction})