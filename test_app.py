from fastapi.testclient import TestClient
from app import app

# We initialize a test client using FastAPI's built-in tools
client = TestClient(app)

def test_metrics_endpoint():
    """Verify that our Prometheus metrics endpoint is online and functioning."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "api_predictions_total" in response.text

def test_single_prediction_valid():
    """Verify that passing correct house data yields a proper price prediction."""
    payload = {
        "MedInc": 8.3,
        "HouseAge": 41.0,
        "AveRooms": 6.9,
        "AveBedrms": 1.0,
        "Population": 322.0,
        "AveOccup": 2.5,
        "Latitude": 37.88,
        "Longitude": -122.23
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    assert "predicted_price" in response.json()
    assert isinstance(response.json()["predicted_price"], float)

def test_single_prediction_invalid():
    """Verify that Pydantic blocks incomplete payloads with a 422 error."""
    payload = {
        "MedInc": 8.3,
        "HouseAge": 41.0
        # Missing geographic details!
    }
    response = client.post("/predict", json=payload)
    # 422 is the standard HTTP code for schema validation failure
    assert response.status_code == 422