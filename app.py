import sys
from fastapi import FastAPI, Request
from pydantic import BaseModel
import joblib
import pandas as pd
from loguru import logger
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import time

# 1. Configure Loguru to write logs in clean JSON format to the terminal
logger.remove()
logger.add(sys.stdout, format="{time} | {level} | {message}", serialize=True)

# 2. Define Prometheus metrics to track requests and processing speed
PREDICTION_COUNTER = Counter("api_predictions_total", "Total number of predictions made", ["type"])
LATENCY_HISTOGRAM = Histogram("api_prediction_latency_seconds", "Time taken to process predictions")

# Define Pydantic Schema
class HouseFeatures(BaseModel):
    MedInc: float
    HouseAge: float
    AveRooms: float
    AveBedrms: float
    Population: float
    AveOccup: float
    Latitude: float
    Longitude: float

# Initialize FastAPI and load model
app = FastAPI(title="Production California House Price Predictor")
model = joblib.load('house_model.joblib')

# Expose /metrics endpoint for Prometheus to collect statistics
@app.get("/metrics")
def get_metrics():
    # ===== YOUR CODE HERE =====
    # Type exactly: return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/predict")
def predict_house(data: HouseFeatures):
    start_time = time.time()
    logger.info("Received single prediction request")
    
    features_dict = data.model_dump()
    input_df = pd.DataFrame([features_dict])
    prediction = model.predict(input_df)[0]
    
    # Record metrics
    PREDICTION_COUNTER.labels(type="single").inc()
    LATENCY_HISTOGRAM.observe(time.time() - start_time)
    
    logger.info(f"Single prediction successful. Result: {prediction}")
    return {"predicted_price": float(prediction)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)