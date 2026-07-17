# =============================================================================
# IMPORT SECTION: Bringing in all our production-grade tools
# =============================================================================

# 1. sys: Standard Python system library.
#    We import this specifically to configure Loguru to write logs to stdout
#    (standard output, i.e., the terminal). This is required for Docker and
#    cloud logging systems (like AWS CloudWatch or GCP Logging) to capture
#    our logs properly.
import sys

# 2. FastAPI: The modern, high-performance web framework.
#    This is the core of our API. It handles routing, validation, and
#    automatically generates interactive documentation at /docs.
#    Request: A class that represents the incoming HTTP request. We import it
#    here, even though we don't explicitly use it in this snippet, because it
#    might be needed for future extensions (e.g., reading headers).
from fastapi import FastAPI, Request

# 3. BaseModel: The "Strict Bouncer" from Pydantic.
#    This is the parent class we inherit from to create our data blueprint
#    (HouseFeatures). It gives us automatic validation and type coercion.
from pydantic import BaseModel

# 4. joblib: The "Unfreezer" / "Defibrillator".
#    We use joblib.load() to bring our frozen pipeline (StandardScaler ->
#    PolynomialFeatures -> Ridge) back to life from house_model.joblib on
#    the hard drive into our computer's RAM.
import joblib

# 5. pandas as pd: The "Spreadsheet Engine".
#    We use Pandas to convert the user's validated JSON data into a DataFrame
#    (a table) that our scikit-learn pipeline can understand and process.
import pandas as pd

# 6. loguru: The "Professional Logger" (replaces print()).
#    Loguru provides structured, timestamped logging with different severity
#    levels (INFO, ERROR, DEBUG). In production, we configure it to output
#    JSON format, which is easily parsed by log aggregation tools like
#    Datadog, ELK, or AWS CloudWatch.
from loguru import logger

# 7. prometheus_client: The "Metrics Collector".
#    This library exposes Prometheus-compatible metrics (counters, histograms)
#    that monitoring systems (like Prometheus + Grafana) can scrape to track
#    the health and performance of our API over time.
#    - Counter: A metric that only goes up (total number of predictions).
#    - Histogram: A metric that tracks the distribution of values (latency).
#    - generate_latest: The function that renders all metrics into the
#      plain-text format that Prometheus expects.
#    - CONTENT_TYPE_LATEST: The exact HTTP header value for Prometheus metrics.
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# 8. Response: A FastAPI response class.
#    We use this to return a custom HTTP response from our /metrics endpoint
#    with the correct content type (text/plain) for Prometheus.
from fastapi.responses import Response

# 9. time: Standard Python time library.
#    We use time.time() to measure the start and end time of each prediction
#    request, allowing us to calculate the exact latency in seconds.
import time


# =============================================================================
# SECTION 1: LOGURU CONFIGURATION (The "Professional Logger" Setup)
# =============================================================================

# 1a. Remove any default log handlers that Loguru automatically sets up.
#     By default, Loguru prints to stderr in a simple, non-JSON format.
#     We remove this default so we can replace it with our own configuration.
logger.remove()

# 1b. Add a new log handler that writes to sys.stdout (the terminal).
#     - sys.stdout: Standard output (the terminal). This is important because
#       Docker and cloud platforms capture stdout by default.
#     - format="{time} | {level} | {message}": A human-readable format with
#       timestamp, log level (INFO/ERROR), and the actual log message.
#     - serialize=True: This is the CRUCIAL setting for production.
#       It tells Loguru to output logs as valid JSON objects (e.g.,
#       {"time": "2024-01-01", "level": "INFO", "message": "Hello"}).
#       JSON logs are machine-parseable, which is essential for centralized
#       log aggregation tools (Elasticsearch, Datadog, etc.).
logger.add(sys.stdout, format="{time} | {level} | {message}", serialize=True)


# =============================================================================
# SECTION 2: PROMETHEUS METRICS DEFINITION (The "Health Monitors")
# =============================================================================

# 2a. PREDICTION_COUNTER: A "Counter" metric (only goes up).
#     - name: "api_predictions_total" - The name Prometheus will use.
#     - documentation: "Total number of predictions made" - A description.
#     - labelnames=["type"]: We add a "type" label so we can differentiate
#       between "single" and "batch" predictions in our Grafana dashboards.
#     - Usage: When a prediction is made, we call
#       PREDICTION_COUNTER.labels(type="single").inc() to increment it by 1.
PREDICTION_COUNTER = Counter(
    "api_predictions_total",
    "Total number of predictions made",
    ["type"]
)

# 2b. LATENCY_HISTOGRAM: A "Histogram" metric (tracks distribution).
#     - name: "api_prediction_latency_seconds" - The metric name.
#     - documentation: "Time taken to process predictions" - A description.
#     - A Histogram automatically buckets the latency values (e.g., <0.1s,
#       0.1-0.5s, 0.5-1s, >1s). This allows us to calculate percentiles
#       (p50, p95, p99) in Grafana.
#     - Usage: We call LATENCY_HISTOGRAM.observe(elapsed_time) after each
#       prediction to record how long it took.
LATENCY_HISTOGRAM = Histogram(
    "api_prediction_latency_seconds",
    "Time taken to process predictions"
)


# =============================================================================
# SECTION 3: PYDANTIC SCHEMA (The "Strict Bouncer" Blueprint)
# =============================================================================

# This class defines the exact shape of the JSON we expect from the user.
# FastAPI uses this to automatically validate incoming requests.
# If the user sends a string to a float field, omits a required field, or
# sends an out-of-range value, FastAPI will automatically return a 422 error
# BEFORE our function code even runs.
class HouseFeatures(BaseModel):
    """
    The mandatory blueprint for a single house prediction request.
    All fields are required (no defaults) and must be floats.
    """
    MedInc: float
    HouseAge: float
    AveRooms: float
    AveBedrms: float
    Population: float
    AveOccup: float
    Latitude: float
    Longitude: float


# =============================================================================
# SECTION 4: FASTAPI APP INITIALIZATION & MODEL LOADING
# =============================================================================

# 4a. Initialize our FastAPI app.
#     The 'title' parameter sets the name of our API in the automatic
#     Swagger documentation page (hosted at /docs).
app = FastAPI(title="Production California House Price Predictor")

# 4b. Load our frozen pipeline brain from the hard drive into RAM.
#     - This line runs ONCE when the server starts.
#     - joblib.load() reads the file 'house_model.joblib' from the current
#       folder and reconstructs the exact Pipeline object.
#     - The pipeline contains the StandardScaler, PolynomialFeatures, and
#       trained Ridge model all in one object.
#     - This 'model' variable sits in memory and waits for requests.
#     - IMPORTANT: If this file is missing, the server will crash immediately
#       on startup (which is good, because it catches the error early).
model = joblib.load('house_model.joblib')


# =============================================================================
# SECTION 5: THE /metrics ENDPOINT (The "Expose Health Stats" Door)
# =============================================================================

# This endpoint is a standard requirement for any production service.
# Prometheus (a monitoring system) continuously scrapes (polls) this endpoint
# to collect metrics about your API's performance and usage.
@app.get("/metrics")
def get_metrics():
    """
    Exposes Prometheus metrics in the format that Prometheus scrapers expect.
    Returns the raw metrics data as plain text with the correct content-type header.
    """
    # ===== YOUR CODE HERE =====
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
    #
    # WHAT THE MISSING LINE DOES:
    # - generate_latest(): This function scans all registered Prometheus
    #   metrics (our Counter and Histogram) and renders them into the
    #   plain-text format that Prometheus understands.
    # - Response(...): We wrap this generated text in a FastAPI Response object.
    # - content: The raw metrics text.
    # - media_type=CONTENT_TYPE_LATEST: This sets the HTTP header
    #   "Content-Type: text/plain; version=0.0.4; charset=utf-8". This tells
    #   Prometheus that the response is in the correct metrics format.
    # - Without this endpoint, you would have no way to monitor your API's
    #   traffic and performance in production.


# =============================================================================
# SECTION 6: THE SINGLE PREDICTION ENDPOINT (The "Main Door")
# =============================================================================

# This endpoint accepts a single house (as JSON) and returns a single price.
@app.post("/predict")
def predict_house(data: HouseFeatures):
    """
    Endpoint that accepts one house's features and returns its predicted price.
    Args:
        data (HouseFeatures): A validated JSON object containing all 8 features.
    Returns:
        dict: A JSON response containing the predicted house price.
    """
    
    # --- Step 1: Start the timer for latency measurement ---
    # time.time() returns the current time in seconds since the epoch (Jan 1, 1970).
    # We capture this at the very beginning of the function so we can calculate
    # exactly how long the prediction took at the end.
    start_time = time.time()
    
    # --- Step 2: Log the incoming request ---
    # logger.info() writes a log message with severity "INFO".
    # Because we configured Loguru with serialize=True, this will be output
    # as a JSON object with timestamp and the message.
    # This is useful for debugging and tracking who is using the API.
    logger.info("Received single prediction request")
    
    # --- Step 3: Convert the validated Pydantic object to a dictionary ---
    # data.model_dump() (formerly .dict()) turns the Pydantic object into a
    # plain Python dict. Example: {'MedInc': 8.3, 'HouseAge': 41, ...}
    features_dict = data.model_dump()
    
    # --- Step 4: Convert the dictionary to a Pandas DataFrame ---
    # We wrap the dict in a list ([features_dict]) to tell Pandas:
    # "This dictionary represents ONE row of data."
    # If we didn't use the brackets, Pandas would misinterpret the keys
    # (MedInc, HouseAge) as row names instead of column names, breaking the model.
    input_df = pd.DataFrame([features_dict])
    
    # --- Step 5: Let our trained brain make the prediction ---
    # model.predict(input_df): Passes the 1-row DataFrame to the pipeline.
    # The pipeline automatically scales, creates polynomial features, and
    # runs the Ridge regression.
    # .predict() returns a NumPy array (e.g., [4.526]).
    # [0] grabs the first (and only) element from that array.
    prediction = model.predict(input_df)[0]
    
    # --- Step 6: Record the metrics ---
    # 6a. Increment the total prediction counter by 1.
    #     .labels(type="single") adds a label called "type" with value "single".
    #     This allows us to filter metrics in Grafana between single and batch predictions.
    PREDICTION_COUNTER.labels(type="single").inc()
    
    # 6b. Calculate the elapsed time and record it in the Histogram.
    #     time.time() - start_time gives the number of seconds the function took.
    #     The Histogram automatically buckets this value and stores it.
    LATENCY_HISTOGRAM.observe(time.time() - start_time)
    
    # --- Step 7: Log the successful prediction ---
    # We log the predicted value so we have a record of what the model output.
    # This is extremely helpful for auditing and debugging in production.
    logger.info(f"Single prediction successful. Result: {prediction}")
    
    # --- Step 8: Return the prediction back to the user ---
    # float(prediction) converts the numpy.float64 to a standard Python float
    # to ensure JSON serialization works perfectly.
    return {"predicted_price": float(prediction)}


# =============================================================================
# SECTION 7: THE DEVELOPMENT SERVER STARTER
# =============================================================================

# This is the standard Python pattern: "If this file is run directly
# (i.e., by typing 'python app.py' in the terminal), then execute the code
# inside this block."
# If this file is imported as a module into another script, this block does NOT run.
if __name__ == "__main__":
    
    # Import uvicorn locally inside this block.
    # Uvicorn is the "Lightning-Fast ASGI Engine" that actually runs our FastAPI code.
    import uvicorn
    
    # Start the Uvicorn server with our application.
    # "app:app": The first "app" is the filename (app.py), the second "app" is
    #            the variable name inside that file (our FastAPI instance).
    # host="127.0.0.1": Only listen on localhost (same computer).
    # port=5000: Listen on port 5000.
    # reload=True: Development mode. Auto-restart the server when code changes.
    #              WARNING: This should NEVER be True in production!
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)