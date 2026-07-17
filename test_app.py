# =============================================================================
# COMMENTARY ON THE TEST FILE CODE BELOW
# =============================================================================
# This is a Pytest test file. It contains automated tests that verify our
# FastAPI application works correctly.
# Pytest automatically discovers and runs any functions in this file that
# start with the prefix "test_".
# This file is executed by GitHub Actions in our CI/CD pipeline whenever
# we push code or open a Pull Request.
# =============================================================================


# -----------------------------------------------------------------------------
# LINE 1: Import FastAPI's built-in test client
# -----------------------------------------------------------------------------
# from fastapi.testclient import TestClient
#
# WHAT IT DOES:
# - "TestClient" is a special tool provided by FastAPI for testing.
# - It creates a simulated HTTP client that can send requests to your
#   FastAPI application WITHOUT actually starting a real web server.
# - This is incredibly fast and doesn't require opening network ports.
# - It works by calling your FastAPI app directly in memory, making it
#   perfect for integration testing.
# - It behaves exactly like the "requests" library, but runs entirely
#   in-process without needing a running server.
from fastapi.testclient import TestClient

# -----------------------------------------------------------------------------
# LINE 2: Import the FastAPI application instance
# -----------------------------------------------------------------------------
# from app import app
#
# WHAT IT DOES:
# - This imports the "app" variable from your "app.py" file.
# - The "app" variable is the FastAPI instance you created with
#   `app = FastAPI(title="Production California House Price Predictor")`.
# - By importing it, we give the TestClient access to all your routes
#   ( /predict, /predict/batch, /metrics, etc.).
# - This is the actual production code being tested, not a mock or stub.
from app import app

# -----------------------------------------------------------------------------
# LINE 3: A comment explaining the next line's purpose
# -----------------------------------------------------------------------------
# # We initialize a test client using FastAPI's built-in tools
#
# WHAT IT DOES:
# - A comment for human readers explaining that we are creating the test client.
# - It explicitly states that this is using FastAPI's built-in tools, which
#   is important for understanding where the testing capability comes from.
# We initialize a test client using FastAPI's built-in tools

# -----------------------------------------------------------------------------
# LINE 4: Instantiate the test client with our application
# -----------------------------------------------------------------------------
# client = TestClient(app)
#
# WHAT IT DOES:
# - "TestClient(app)" creates a test client instance that is bound to
#   your FastAPI application.
# - We store this instance in a variable called "client".
# - From now on, we can use "client.get()", "client.post()", etc., to
#   simulate HTTP requests to your API.
# - The client automatically handles:
#   - URL parsing
#   - Request serialization (turning Python dicts into JSON)
#   - Response deserialization (turning JSON back into Python dicts)
# - It does not actually bind to a network port, so there is no risk of
#   port conflicts or needing to run the server separately.
client = TestClient(app)


# =============================================================================
# SECTION 1: TEST THE /metrics ENDPOINT
# =============================================================================

# -----------------------------------------------------------------------------
# LINE 7-8: The test function definition and docstring
# -----------------------------------------------------------------------------
# def test_metrics_endpoint():
#     """Verify that our Prometheus metrics endpoint is online and functioning."""
#
# WHAT IT DOES:
# - This is a Python function named "test_metrics_endpoint".
# - Pytest automatically discovers and executes ANY function that starts
#   with "test_".
# - The docstring (triple-quoted string) describes what this test does.
#   This docstring appears in Pytest's verbose output and helps with
#   documentation.
#
# What this test verifies:
#   - The /metrics endpoint is reachable (returns HTTP 200).
#   - The response contains the "api_predictions_total" metric text,
#     confirming that the Prometheus integration is working correctly.
def test_metrics_endpoint():
    """Verify that our Prometheus metrics endpoint is online and functioning."""
    
    # -------------------------------------------------------------------------
    # LINE 9: Send a GET request to the /metrics endpoint
    # -------------------------------------------------------------------------
    # response = client.get("/metrics")
    #
    # WHAT IT DOES:
    # - "client.get()" sends an HTTP GET request to the specified path.
    # - The path "/metrics" corresponds to the endpoint defined in your app.py:
    #   @app.get("/metrics")
    #   def get_metrics():
    # - The TestClient sends the request, your FastAPI app processes it,
    #   and the result is stored in the "response" variable.
    response = client.get("/metrics")
    
    # -------------------------------------------------------------------------
    # LINE 10: Assert that the response status code is 200 OK
    # -------------------------------------------------------------------------
    # assert response.status_code == 200
    #
    # WHAT IT DOES:
    # - "assert" is a Python statement that checks if a condition is True.
    # - If the condition is True, the test continues.
    # - If the condition is False, Pytest raises an AssertionError and
    #   marks this test as FAILED.
    # - "response.status_code == 200" checks that the server returned a
    #   200 OK status code, meaning the endpoint is working correctly.
    # - If the endpoint was missing or crashed, the status code would be
    #   404 (Not Found) or 500 (Internal Server Error), and the test would fail.
    assert response.status_code == 200
    
    # -------------------------------------------------------------------------
    # LINE 11: Assert that the response text contains the expected metric name
    # -------------------------------------------------------------------------
    # assert "api_predictions_total" in response.text
    #
    # WHAT IT DOES:
    # - "response.text" is the raw plain-text body of the HTTP response.
    # - "api_predictions_total" is the name of the counter metric we defined
    #   in app.py: PREDICTION_COUNTER = Counter("api_predictions_total", ...)
    # - This assertion checks that the /metrics endpoint is actually
    #   returning the Prometheus metrics we defined, not just an empty
    #   response or some other text.
    # - This proves that your Prometheus integration is working correctly.
    assert "api_predictions_total" in response.text


# =============================================================================
# SECTION 2: TEST THE SINGLE PREDICTION ENDPOINT (VALID DATA)
# =============================================================================

# -----------------------------------------------------------------------------
# LINES 14-28: The test function for valid single prediction
# -----------------------------------------------------------------------------
# def test_single_prediction_valid():
#     """Verify that passing correct house data yields a proper price prediction."""
#
# WHAT IT DOES:
# - This test validates the "happy path" of your API.
# - It sends a complete, valid JSON payload to /predict and verifies that
#   the API responds correctly.
# - This is the most critical test because it represents the normal
#   expected usage of your application.
def test_single_prediction_valid():
    """Verify that passing correct house data yields a proper price prediction."""
    
    # -------------------------------------------------------------------------
    # LINE 15-25: Define the test payload (a valid house)
    # -------------------------------------------------------------------------
    # payload = {
    #     "MedInc": 8.3,
    #     "HouseAge": 41.0,
    #     "AveRooms": 6.9,
    #     "AveBedrms": 1.0,
    #     "Population": 322.0,
    #     "AveOccup": 2.5,
    #     "Latitude": 37.88,
    #     "Longitude": -122.23
    # }
    #
    # WHAT IT DOES:
    # - This is a Python dictionary that represents a complete, valid
    #   request body for the /predict endpoint.
    # - It contains ALL 8 required fields from the HouseFeatures Pydantic model.
    # - All values are valid floats within expected ranges (e.g., Latitude 37.88).
    # - This payload is designed to pass ALL validation checks and produce
    #   a successful prediction.
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
    
    # -------------------------------------------------------------------------
    # LINE 26: Send a POST request to /predict with the payload
    # -------------------------------------------------------------------------
    # response = client.post("/predict", json=payload)
    #
    # WHAT IT DOES:
    # - "client.post()" sends an HTTP POST request to the specified path.
    # - "json=payload" tells the TestClient to send the dictionary as a
    #   JSON-encoded request body. It automatically sets the
    #   Content-Type header to "application/json".
    # - The request is routed to your @app.post("/predict") endpoint.
    # - FastAPI uses Pydantic to validate the payload against the
    #   HouseFeatures model. Because the payload is valid, the validation
    #   passes and your predict_house() function executes.
    response = client.post("/predict", json=payload)
    
    # -------------------------------------------------------------------------
    # LINE 27: Assert that the status code is 200 OK
    # -------------------------------------------------------------------------
    # assert response.status_code == 200
    #
    # WHAT IT DOES:
    # - Verifies that the request was processed successfully.
    # - A 200 status code confirms that:
    #   1. The endpoint exists.
    #   2. The payload passed Pydantic validation.
    #   3. The model made a prediction without crashing.
    assert response.status_code == 200
    
    # -------------------------------------------------------------------------
    # LINE 28: Assert that the response JSON contains the "predicted_price" field
    # -------------------------------------------------------------------------
    # assert "predicted_price" in response.json()
    #
    # WHAT IT DOES:
    # - "response.json()" parses the JSON response body into a Python dictionary.
    # - This assertion checks that the response dictionary contains a key
    #   called "predicted_price".
    # - In your app.py, the endpoint returns:
    #   {"predicted_price": float(prediction)}
    # - If the response was missing this key (e.g., if you changed the
    #   return format), this test would catch that and fail.
    assert "predicted_price" in response.json()
    
    # -------------------------------------------------------------------------
    # LINE 29: Assert that the predicted price is a float
    # -------------------------------------------------------------------------
    # assert isinstance(response.json()["predicted_price"], float)
    #
    # WHAT IT DOES:
    # - "isinstance()" checks the type of a Python object.
    # - "response.json()["predicted_price"]" accesses the predicted price
    #   value from the response dictionary.
    # - This assertion verifies that the predicted price is a Python float,
    #   not a string, integer, or None.
    # - FastAPI automatically converts the numpy.float64 from your model
    #   to a standard Python float via your explicit `float(prediction)` cast.
    # - If you forgot the `float()` cast, numpy.float64 would still be
    #   JSON-serializable, but this test ensures you explicitly handle it.
    assert isinstance(response.json()["predicted_price"], float)


# =============================================================================
# SECTION 3: TEST THE SINGLE PREDICTION ENDPOINT (INVALID DATA)
# =============================================================================

# -----------------------------------------------------------------------------
# LINES 32-42: The test function for invalid single prediction (422)
# -----------------------------------------------------------------------------
# def test_single_prediction_invalid():
#     """Verify that Pydantic blocks incomplete payloads with a 422 error."""
#
# WHAT IT DOES:
# - This test validates the "error handling" or "sad path" of your API.
# - It sends an INCOMPLETE payload to /predict and verifies that
#   FastAPI/Pydantic correctly rejects it with a 422 Unprocessable Entity
#   error.
# - This proves that your Pydantic model is enforcing all required fields.
def test_single_prediction_invalid():
    """Verify that Pydantic blocks incomplete payloads with a 422 error."""
    
    # -------------------------------------------------------------------------
    # LINE 33-36: Define the invalid payload (missing critical fields)
    # -------------------------------------------------------------------------
    # payload = {
    #     "MedInc": 8.3,
    #     "HouseAge": 41.0
    #     # Missing geographic details!
    # }
    #
    # WHAT IT DOES:
    # - This payload is MISSING 6 out of 8 required fields.
    # - It only contains "MedInc" and "HouseAge".
    # - Crucially, it does NOT contain "AveRooms", "AveBedrms",
    #   "Population", "AveOccup", "Latitude", or "Longitude".
    # - The comment "# Missing geographic details!" serves as a reminder
    #   to the developer reading the test why this payload is invalid.
    payload = {
        "MedInc": 8.3,
        "HouseAge": 41.0
        # Missing geographic details!
    }
    
    # -------------------------------------------------------------------------
    # LINE 37: Send a POST request to /predict with the invalid payload
    # -------------------------------------------------------------------------
    # response = client.post("/predict", json=payload)
    #
    # WHAT IT DOES:
    # - Sends the incomplete payload to the /predict endpoint.
    # - FastAPI receives the request and attempts to validate it against
    #   the HouseFeatures model.
    # - Because the Pydantic model defines all fields as REQUIRED (no defaults),
    #   the validation immediately fails.
    # - The validation failure occurs BEFORE your predict_house() function
    #   is ever called.
    response = client.post("/predict", json=payload)
    
    # -------------------------------------------------------------------------
    # LINE 38-40: Comment and assert that the status code is 422
    # -------------------------------------------------------------------------
    # # 422 is the standard HTTP code for schema validation failure
    # assert response.status_code == 422
    #
    # WHAT IT DOES:
    # - "422 Unprocessable Entity" is the standard HTTP status code that
    #   FastAPI automatically returns when Pydantic validation fails.
    # - This assertion verifies that your API correctly rejects the
    #   invalid payload instead of crashing or returning a 200 OK with
    #   a garbage response.
    # - This confirms that your "Bouncer" (Pydantic) is working as expected.
    # 422 is the standard HTTP code for schema validation failure
    assert response.status_code == 422

# =============================================================================
# END OF TEST FILE
# =============================================================================
# HOW TO RUN THESE TESTS LOCALLY:
# 1. Make sure you are in your project folder with (venv) activated.
# 2. Install pytest and httpx: pip install pytest httpx
# 3. Run the command: pytest test_app.py -v
#    (The -v flag gives you verbose output showing each test result)
# 4. You should see output like:
#    test_metrics_endpoint PASSED
#    test_single_prediction_valid PASSED
#    test_single_prediction_invalid PASSED
#    ===================== 3 passed in 0.5s =====================
#
# HOW THESE TESTS RUN IN CI/CD (GitHub Actions):
# 1. The CI/CD pipeline installs dependencies, including pytest.
# 2. It runs the exact same command: pytest test_app.py
# 3. If ANY test fails, the entire pipeline fails, preventing the
#    broken code from being merged into the main branch.
# =============================================================================