from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, create_model
import uvicorn
import joblib
import numpy as np
import os
import pandas as pd

app = FastAPI(title="Network Intrusion Detection API")

# Allow CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Models independently
MODELS_DIR = "../models"

def safe_load(filename):
    path = os.path.join(MODELS_DIR, filename)
    if os.path.exists(path):
        try:
            return joblib.load(path)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
    return None

rf_model = safe_load('random_forest.pkl')
dnn_model = safe_load('dnn_model.pkl')
autoencoder = safe_load('autoencoder_model.pkl')
threshold = safe_load('autoencoder_threshold.pkl')
scaler = safe_load('scaler.pkl')
label_encoder = safe_load('label_encoder.pkl')

print(f"Loaded Models -> RF: {rf_model is not None}, DNN: {dnn_model is not None}, Autoencoder: {autoencoder is not None}, Scaler: {scaler is not None}")


# We need a dynamic Pydantic model because there are 78 features
# We'll just load the feature columns from the scaler or standard list
class NetworkFlowFeatures(BaseModel):
    features: list[float]

@app.get("/health")
def health_check():
    return {"status": "ok", "models_loaded": rf_model is not None}

@app.post("/predict")
def predict_flow(flow: NetworkFlowFeatures, model_type: str = "rf"):
    if not scaler:
        raise HTTPException(status_code=500, detail="Models are not loaded on server.")
        
    try:
        # 1. Scale input
        X_input = np.array(flow.features).reshape(1, -1)
        
        if X_input.shape[1] != scaler.n_features_in_:
            raise HTTPException(status_code=400, detail=f"Expected {scaler.n_features_in_} features, got {X_input.shape[1]}")
            
        X_scaled = scaler.transform(X_input)
        
        # 2. Prediction based on selected model
        if model_type == "rf" and rf_model:
            pred_encoded = rf_model.predict(X_scaled)[0]
            probability = np.max(rf_model.predict_proba(X_scaled)[0])
        elif model_type == "dnn" and dnn_model:
            pred_encoded = dnn_model.predict(X_scaled)[0]
            probability = np.max(dnn_model.predict_proba(X_scaled)[0])
        else:
            raise HTTPException(status_code=400, detail="Invalid model type requested.")
            
        prediction_label = label_encoder.inverse_transform([pred_encoded])[0]
        
        # 3. Anomaly detection score
        if autoencoder:
            reconstruction = autoencoder.predict(X_scaled)
            mse = np.mean(np.power(X_scaled - reconstruction, 2))
            is_anomaly = bool(mse > threshold)
        else:
            mse, is_anomaly = 0.0, False
            
        return {
            "prediction_label": prediction_label,
            "probability": round(float(probability), 4),
            "anomaly_score": round(float(mse), 4),
            "is_anomaly": is_anomaly,
            "threshold": round(float(threshold), 4)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
