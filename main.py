from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import torch
import joblib
import numpy as np
import pandas as pd

from models.disease_model import DiseaseModel

class SymptomsInput(BaseModel):
    symptoms: List[int]
    

app = FastAPI()


classes = joblib.load('model/label_classes.pkl')

# Load model
input_dim = 377   
output_dim = len(classes)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = DiseaseModel(input_dim, output_dim).to(device)
model.load_state_dict(torch.load('model/disease_model.pth', map_location=device))
model.eval()  


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prediction endpoint
@app.post("/predict")
async def predict(input_data: SymptomsInput):
    if len(input_data.symptoms) != 377:
        raise HTTPException(status_code=400, detail="Expected 377 symptom values.")

    try:
        X_tensor = torch.tensor([input_data.symptoms], dtype=torch.float32).to(device)
        
        with torch.no_grad():
            outputs = model(X_tensor)
            predictions = (outputs > 0.5).cpu().numpy()

        predicted_diseases = [list(classes[predictions[0].astype(bool)])]

        return {"predicted_diseases": predicted_diseases}

    except Exception as e:
        return {"error": str(e)}