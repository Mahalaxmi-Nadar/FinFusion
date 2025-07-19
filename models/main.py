from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI()

# Load models and label mappings
recommendation_model = joblib.load("models/Recommendation_model.pkl")
recommendation_labels = joblib.load("models/Recommendation_labels.pkl")

term_model = joblib.load("models/Term_Suggested_model.pkl")
term_labels = joblib.load("models/Term_Suggested_labels.pkl")

risk_model = joblib.load("models/Risk_Level_model.pkl")
risk_labels = joblib.load("models/Risk_Level_labels.pkl")

# Define input model


@app.post("/recommend")
def get_investment_recommendation(data: InvestmentRequest):
    # Prepare input as DataFrame
    df = pd.DataFrame([data.dict()])

    # Predict from all 3 models
    rec = recommendation_model.predict(df)[0]
    term = term_model.predict(df)[0]
    risk = risk_model.predict(df)[0]

    # Decode predictions using label maps
    result = {
        "Recommendation": recommendation_labels[rec],
        "Term_Suggested": term_labels[term],
        "Risk_Level": risk_labels[risk]
    }

    return result
