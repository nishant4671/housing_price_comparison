# ====================================================================
# IMPORT SECTION: Bringing in our high-performance production tools
# ====================================================================

# 1. FastAPI: The "Supercharged Blueprint" framework.
#    This is the replacement for Flask. It automatically generates
#    interactive API documentation (/docs) and handles validation
#    using Pydantic models. It runs on ASGI (asynchronous) which
#    allows it to handle thousands of requests simultaneously.
from fastapi import FastAPI, HTTPException

# 2. BaseModel & Field: The "Strict Bouncer" and "Rule Enforcer".
#    BaseModel: The parent class we inherit to create our data Blueprint.
#    Field: The tool that adds extra constraints like 'must be > 0'
#    or 'must be between 32 and 42'. This eliminates ALL manual if/else checks.
from pydantic import BaseModel, Field

# 3. List: A standard Python type hint.
#    We use this to tell FastAPI that the user is sending us an ARRAY
#    of houses for batch prediction (e.g., [house1, house2, house3]).
from typing import List

# 4. joblib: The "Defibrillator / Unfreezer".
#    We already used this to freeze our trained pipeline in train_model.py.
#    Now we use joblib.load() to bring that frozen pipeline back to life
#    from the hard drive into our computer's RAM. The pipeline contains
#    the Scaler, the PolynomialFeatures, and the Ridge model all in one object.
import joblib

# 5. pandas as pd: The "Spreadsheet Engine".
#    Even though our incoming data is validated by Pydantic, our
#    scikit-learn pipeline expects the data as a DataFrame (a table).
#    We use pandas to convert the validated Python dictionary into
#    a single-row DataFrame that our pipeline can eat.
import pandas as pd

# 6. loguru: The "Professional Logger" (replaces print()).
#    In production, print() statements are useless because they don't
#    have timestamps, log levels (INFO, ERROR, DEBUG), or standard formats.
#    loguru logs to stdout (which Docker can capture) and looks professional.
#    We install it with: pip install loguru
from loguru import logger

# ====================================================================
# SECTION 1: LOADING THE FROZEN BRAIN
# ====================================================================

# 1a. Tell the user (and the logs) that we are starting the loading process.
logger.info("Starting the API server. Loading the frozen ML pipeline...")

# 1b. The Heart Transplant.
#     joblib.load() reads the binary file 'house_model.joblib' from our
#     hard drive, reconstructs the exact Python object (the full Pipeline
#     containing Scaler + PolynomialFeatures + Ridge), and stores it in RAM.
#     This is done ONCE when the server starts. The model sits in memory
#     patiently waiting for the API to receive requests.
#     WARNING: If this file is missing, the server will crash immediately
#     on startup (which is actually good, because we catch it early).
model = joblib.load('house_model.joblib')

# 1c. Confirm the model is alive and ready in the logs.
logger.success("✅ ML Pipeline successfully loaded into memory!")

# ====================================================================
# SECTION 2: PYDANTIC SCHEMA (The "Strict Bouncer" Blueprint)
# ====================================================================

# This is our "Checklist" or "Blueprint" for incoming data.
# We define the shape of the JSON we expect from the user.
# FastAPI uses this to automatically validate, parse, and reject
# malformed requests BEFORE our function code ever runs.

class HouseFeatures(BaseModel):
    """
    A Pydantic model that represents the 8 features required
    for a house price prediction.

    FastAPI will automatically:
    - Check that ALL required fields are present.
    - Check that they are the correct type (float).
    - Check the range constraints (e.g., Latitude between 32 and 42).
    - Convert strings like "8.3" to a float automatically.
    """
    
    # MedInc (Median Income): Must be a float, and must be greater than 0.
    # The '...' means this field is REQUIRED. The user cannot omit it.
    # 'description' adds a nice label to the automatic Swagger docs.
    MedInc: float = Field(..., gt=0, description="Median income in the block (in tens of thousands)")
    
    # HouseAge: Must be a float, greater than or equal to 0.
    HouseAge: float = Field(..., ge=0, description="Median age of houses in the block")
    
    # AveRooms: Average rooms. Must be greater than 0 (you can't have 0 rooms).
    AveRooms: float = Field(..., gt=0, description="Average number of rooms per house")
    
    # AveBedrms: Average bedrooms. Must be greater than 0.
    AveBedrms: float = Field(..., gt=0, description="Average number of bedrooms per house")
    
    # Population: Number of people in the block. Must be >= 0.
    Population: float = Field(..., ge=0, description="Population of the block")
    
    # AveOccup: Average occupants per house. Must be > 0.
    AveOccup: float = Field(..., gt=0, description="Average number of occupants per house")
    
    # Latitude: Geographical latitude. In California, this is roughly 32 to 42.
    # 'ge=32' means "greater than or equal to 32".
    # 'le=42' means "less than or equal to 42".
    # If the user sends 90.0, Pydantic will reject it automatically.
    Latitude: float = Field(..., ge=32, le=42, description="Latitude of the block (32-42 for CA)")
    
    # Longitude: Geographical longitude. (California is roughly -124 to -114,
    # but we don't enforce a strict range here, just that it must be a float).
    Longitude: float = Field(..., description="Longitude of the block")


# ====================================================================
# SECTION 3: FASTAPI APPLICATION INSTANCE (The "Architect")
# ====================================================================

# 3a. Create the FastAPI app instance.
#     This is the "Architect" or "Manager" object.
#     We will attach our endpoints (routes) to this variable.
#     The title and version are used to generate the automatic
#     documentation at /docs and /redoc.
app = FastAPI(
    title="California Housing Price Predictor API",
    description="A production-grade ML API that predicts house prices using a Ridge Regression model with Polynomial Features.",
    version="2.0.0"
)

# ====================================================================
# SECTION 4: HEALTH CHECK ENDPOINT (The "Are You Alive?" Door)
# ====================================================================

# This is the most basic endpoint. Cloud services (like Kubernetes or AWS)
# continuously hit this endpoint to check if the server is still alive.
# If this endpoint returns a 200 OK, the service is considered "healthy".
# If it returns an error, the cloud service will automatically restart the server.

@app.get("/")
async def health_check():
    """
    Health check endpoint.
    Returns a simple JSON message to confirm the API is running.
    """
    # Log that someone checked the health (good for debugging).
    logger.debug("Health check endpoint was called.")
    return {
        "status": "healthy",
        "message": "House Price Predictor API is up and running!",
        "model_loaded": model is not None
    }


# ====================================================================
# SECTION 5: SINGLE PREDICTION ENDPOINT (The "Predict One House" Door)
# ====================================================================

# This is the main door where users send ONE house to get ONE price.
# We use POST because the user is SENDING data to us.

@app.post("/predict")
async def predict_single(house: HouseFeatures):
    """
    Predict the price of a SINGLE house.

    Args:
        house (HouseFeatures): A valid JSON object containing all 8 features.

    Returns:
        dict: A JSON object with the predicted price in hundreds of thousands.
    """
    
    # --- Step 1: Logging the incoming request ---
    # Loguru logs this to the console with a timestamp. This helps us track
    # who is using the API and when.
    logger.info(f"Received single prediction request: {house}")
    
    # --- Step 2: Convert the validated Pydantic model to a DataFrame ---
    # house.model_dump() converts the Pydantic object into a Python dictionary.
    # e.g., {'MedInc': 8.3, 'HouseAge': 41, ...}
    # We wrap it in [] to tell Pandas: "Treat this dictionary as a SINGLE ROW of a table."
    # If we used pd.DataFrame(house.model_dump()) without brackets, Pandas would
    # treat the keys (MedInc, HouseAge) as the ROW NAMES instead of COLUMN NAMES,
    # which would completely break the model.
    input_df = pd.DataFrame([house.model_dump()])
    
    # --- Step 3: Hand the table to the Pipeline for prediction ---
    # Our 'model' is the full pipeline (Scaler -> Poly -> Ridge).
    # We pass the DataFrame. The pipeline automatically:
    # 1. Scales the numbers using the mean/std it learned during training.
    # 2. Creates the polynomial (squared) features.
    # 3. Runs the Ridge regression to get the price.
    # .predict() returns a list/array. Even though we only gave it 1 row,
    # it returns a list with 1 number inside. We grab the first (and only) element.
    prediction = model.predict(input_df)[0]
    
    # --- Step 4: Format the response ---
    # Our training data target (MedHouseVal) is in units of $100,000.
    # So a prediction of 4.5 means $450,000.
    # We convert the numpy float64 to a standard Python float to make it JSON serializable.
    logger.success(f"Prediction successful: {float(prediction)}")
    return {
        "predicted_price_in_hundred_thousands": float(prediction),
        "status": "success"
    }


# ====================================================================
# SECTION 6: BATCH PREDICTION ENDPOINT (The "Predict Many Houses" Door)
# ====================================================================

# This is the premium endpoint. Instead of sending ONE house, the user
# sends a LIST of houses. The model predicts all of them at once,
# which is much more efficient than calling /predict 100 times separately.
# NOTE: The type hint List[HouseFeatures] tells FastAPI: "The request body
# must be a JSON ARRAY, and each item in the array must match HouseFeatures."

@app.post("/predict_batch")
async def predict_batch(houses: List[HouseFeatures]):
    """
    Predict the prices of MULTIPLE houses at once (Batch Prediction).

    Args:
        houses (List[HouseFeatures]): A JSON array of house objects.

    Returns:
        dict: A JSON object with an array of predicted prices.
    """
    
    # --- Step 1: Logging the incoming request ---
    logger.info(f"Received batch prediction request for {len(houses)} houses.")
    
    # --- Step 2: Convert the list of validated Pydantic models to a DataFrame ---
    # This is a classic Python list comprehension.
    # For each house object in the 'houses' list, we call .model_dump()
    # to convert it to a dictionary.
    # So we get a list of dictionaries: [{'MedInc': 8.3, ...}, {'MedInc': 3.5, ...}]
    dict_list = [house.model_dump() for house in houses]
    
    # We pass this list of dictionaries to pd.DataFrame.
    # Pandas will automatically turn it into a table where each dictionary
    # becomes a SINGLE ROW. This creates a beautiful table with 8 columns and N rows.
    input_df = pd.DataFrame(dict_list)
    
    # --- Step 3: Ask the model to predict all rows at once ---
    # The pipeline handles the entire batch in one go using vectorized operations.
    # This is EXTREMELY fast compared to looping through each house.
    # .predict() returns a NumPy array (e.g., [4.5, 2.1, 3.8]).
    predictions = model.predict(input_df)
    
    # --- Step 4: Convert the NumPy array to a list of Python floats ---
    # predictions.tolist() converts the numpy array into a clean Python list.
    # This is required so FastAPI can automatically convert it to JSON.
    predictions_list = predictions.tolist()
    
    logger.success(f"Batch prediction successful for {len(predictions_list)} houses.")
    return {
        "predictions": predictions_list,
        "count": len(predictions_list),
        "status": "success"
    }


# ====================================================================
# SECTION 7: EXCEPTION HANDLER (The "Polite Error Response")
# ====================================================================

# While Pydantic automatically handles 422 validation errors, there might be
# other unexpected errors (e.g., the model file is corrupted, or memory runs out).
# This is a global "Catch-All" safety net. If ANY exception bubbles up
# that we didn't handle, this function will catch it and return a clean
# 500 Internal Server Error instead of crashing the whole server.

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for any unhandled exceptions.
    This prevents the server from crashing and logs the error for debugging.
    """
    # Log the full error to the console with traceback for the developer.
    # In production, this would also send an alert to a monitoring system.
    logger.error(f"Unhandled exception occurred: {exc}")
    
    # Return a clean, standard JSON error response to the user.
    # We intentionally DO NOT expose the full traceback to the user for security reasons.
    return {
        "error": "An unexpected internal server error occurred. Please try again later.",
        "status": "error"
    }, 500

# ====================================================================
# END OF FILE
# ====================================================================
# HOW TO RUN THIS FILE:
# 1. Make sure you are in your project folder with (venv) activated.
# 2. Make sure house_model.joblib exists in the same folder.
# 3. Run the command: uvicorn app:app --reload
# 4. Open your browser to http://127.0.0.1:8000/docs to see the interactive docs.
# ====================================================================













# =============================================================================
# COMMENTARY ON THE CODE BELOW
# =============================================================================
# Note: The provided code snippet does not include the import statements
# (e.g., from fastapi import FastAPI, import joblib, etc.). However, for this
# code to run, those imports must exist at the top of the file. We are
# commenting on the code exactly as it is written here.
# =============================================================================


# -----------------------------------------------------------------------------
# LINE 1: Initialize our FastAPI app
# -----------------------------------------------------------------------------
# app = FastAPI(title="Production California House Price Predictor")
#
# WHAT IT DOES:
# - Creates the main FastAPI application instance.
# - This 'app' object is the core of your web server. It acts as the 
#   "Architect" or "Manager" that will coordinate all incoming requests.
# - The `title` parameter is a meta-data field. It sets the name of your API
#   that will appear at the top of the automatic interactive documentation
#   page (which is hosted at /docs). This helps users understand what your API does.
# - Without this line, you wouldn't have a web application to attach routes to.
app = FastAPI(title="Production California House Price Predictor")

# -----------------------------------------------------------------------------
# LINE 2: Load our newly saved, warning-free pipeline brain
# -----------------------------------------------------------------------------
# model = joblib.load('house_model.joblib')
#
# WHAT IT DOES:
# - This line loads your pre-trained machine learning pipeline from your hard drive.
# - `joblib.load()` is the "Unfreezer" function. It reads the binary file
#   named 'house_model.joblib' from your current project folder, reconstructs
#   the exact Python object (the Pipeline containing StandardScaler, 
#   PolynomialFeatures, and the trained Ridge model), and stores it in RAM.
# - This is a critical step because it brings your "brain" back to life.
# - This line runs ONCE when the server starts. The loaded model sits in memory
#   (in the variable named `model`) and waits for prediction requests.
# - If this file is missing, the server will crash immediately on startup.
model = joblib.load('house_model.joblib')

# -----------------------------------------------------------------------------
# LINE 3: Create our prediction route!
# -----------------------------------------------------------------------------
# @app.post("/predict")
#
# WHAT IT DOES:
# - This is a Python "Decorator". It modifies the function directly below it.
# - It tells FastAPI: "When a user sends an HTTP POST request to the URL path
#   '/predict' (e.g., http://127.0.0.1:5000/predict), run the function
#   defined immediately after this line."
# - The `POST` method is used because the user is sending (submitting) data
#   to the server, rather than just requesting to view a webpage (which would use GET).
# - This line effectively "plugs" your function into the web server's routing table.
@app.post("/predict")

# -----------------------------------------------------------------------------
# LINE 4: We use 'HouseFeatures' to force incoming data to match our schema exactly.
# -----------------------------------------------------------------------------
# def predict_house(data: HouseFeatures):
#
# WHAT IT DOES:
# - This defines the function that will run when someone visits the '/predict' endpoint.
# - `def predict_house(...)`: The name of the function. It could be anything, but 
#   descriptive names are good practice.
# - `data: HouseFeatures`: This is the parameter that will receive the incoming data.
#   - `data` is the variable name.
#   - `: HouseFeatures` is a type hint. It tells FastAPI: "The body of the incoming
#     HTTP request must be a JSON object that matches the 'HouseFeatures' Pydantic model."
#   - FastAPI automatically parses the raw JSON, validates it against the 
#     HouseFeatures blueprint (checking types, required fields, and range 
#     constraints), and if validation passes, it hands you the result as a 
#     Python object assigned to `data`.
#   - If validation fails, FastAPI immediately returns a 422 error to the user
#     and this function is NEVER executed.
def predict_house(data: HouseFeatures):
    
    # -------------------------------------------------------------------------
    # LINE 5: Convert our single data point from the user into a dictionary
    # -------------------------------------------------------------------------
    # features_dict = data.model_dump()
    #
    # WHAT IT DOES:
    # - `data` is a Pydantic object (an instance of HouseFeatures).
    # - `.model_dump()` (formerly `.dict()` in older versions) converts this
    #   Pydantic object into a standard Python dictionary.
    # - Example: If the user sent { "MedInc": 8.3, "HouseAge": 41, ... }, this 
    #   line turns it into a Python dict: {'MedInc': 8.3, 'HouseAge': 41, ...}.
    # - We need a dictionary because Pandas (which we use next) can easily
    #   convert a dictionary into a table (DataFrame).
    features_dict = data.model_dump()
    
    # -------------------------------------------------------------------------
    # LINE 6: Convert that dictionary into a Pandas DataFrame row so our pipeline can read it
    # -------------------------------------------------------------------------
    # input_df = pd.DataFrame([features_dict])
    #
    # WHAT IT DOES:
    # - Our scikit-learn pipeline (`model`) expects input as a 2D table (a DataFrame)
    #   with columns matching the feature names it was trained on.
    # - `pd.DataFrame(...)` is the Pandas function that creates a table.
    # - We pass `[features_dict]` (the dictionary wrapped in a list) to tell Pandas:
    #   "Treat this single dictionary as ONE ROW of data."
    # - If we instead wrote `pd.DataFrame(features_dict)` without the brackets, 
    #   Pandas would misinterpret the keys (MedInc, HouseAge) as row names, 
    #   which would completely break the model.
    # - The result is `input_df`, a beautiful 1-row table with 8 columns 
    #   (e.g., MedInc, HouseAge, etc.)—exactly what the pipeline expects.
    input_df = pd.DataFrame([features_dict])
    
    # -------------------------------------------------------------------------
    # LINE 7: Let our trained brain make the prediction
    # -------------------------------------------------------------------------
    # prediction = model.predict(input_df)[0]
    #
    # WHAT IT DOES:
    # - `model.predict(...)`: Calls the .predict() method on your full pipeline.
    #   The pipeline automatically applies StandardScaler, creates PolynomialFeatures, 
    #   and runs the Ridge regression—all in one go.
    # - `input_df` is passed in. The pipeline processes it.
    # - `.predict()` always returns a NumPy array (a list-like structure), even if
    #   you only predict on 1 row. For example, it might return `[4.526]`.
    # - `[0]` at the end grabs the first and only element from that array, 
    #   extracting the raw predicted value (e.g., `4.526`) and assigning it to 
    #   the variable `prediction`.
    prediction = model.predict(input_df)[0]
    
    # -------------------------------------------------------------------------
    # LINE 8: Return the prediction back to the user
    # -------------------------------------------------------------------------
    # return {"predicted_price": float(prediction)}
    #
    # WHAT IT DOES:
    # - This line sends the response back to the client (the user who made the request).
    # - We create a Python dictionary: `{"predicted_price": float(prediction)}`.
    # - `float(prediction)` converts the prediction (which might be a numpy.float64) 
    #   into a standard Python float. This ensures it is JSON-serializable.
    # - FastAPI automatically takes this Python dictionary, converts it to JSON,
    #   and wraps it in an HTTP response with a 200 OK status code.
    # - The user receives something like: `{"predicted_price": 4.526}`.
    return {"predicted_price": float(prediction)}

# -----------------------------------------------------------------------------
# LINE 9: This runs the web server automatically when we call python app.py
# -----------------------------------------------------------------------------
# if __name__ == "__main__":
#
# WHAT IT DOES:
# - This is a standard Python idiom.
# - `__name__` is a special Python variable. It is automatically set to the
#   string `"__main__"` when the script is executed directly (e.g., by typing
#   `python app.py` in the terminal).
# - If this file is imported as a module into another script (e.g., `import app`),
#   `__name__` will be set to `"app"` (the name of the module), and this block
#   will NOT run.
# - This conditional ensures the server only starts when you run this file directly,
#   not when it is imported elsewhere.
if __name__ == "__main__":
    
    # -------------------------------------------------------------------------
    # LINE 10: Import uvicorn inside the conditional block
    # -------------------------------------------------------------------------
    # import uvicorn
    #
    # WHAT IT DOES:
    # - Imports the Uvicorn library specifically for the purpose of running the server.
    # - We import it here (instead of at the top of the file) to keep the import
    #   local to this specific "start server" block, which is a matter of preference.
    # - Uvicorn is the "Lightning-Fast ASGI Engine" that actually runs your FastAPI code.
    import uvicorn
    
    # -------------------------------------------------------------------------
    # LINE 11: Start the Uvicorn server with our application
    # -------------------------------------------------------------------------
    # uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)
    #
    # WHAT IT DOES:
    # - `uvicorn.run()` is the command that actually starts the web server process.
    # - It takes several critical arguments:
    # 
    #   "app:app" (First Argument):
    #     - The first "app" is the name of the Python file (app.py) without the .py.
    #     - The second "app" is the variable name inside that file where we 
    #       created our FastAPI instance (app = FastAPI(...)).
    #     - This string tells Uvicorn exactly what to load and run.
    # 
    #   host="127.0.0.1" (Second Argument):
    #     - This tells the server to only listen for requests coming from the 
    #       same computer (localhost). 
    #     - "127.0.0.1" is the loopback IP address.
    #     - If you want other devices on your network to access your API, you
    #       would change this to "0.0.0.0".
    # 
    #   port=5000 (Third Argument):
    #     - This sets the "door number" on your computer. 
    #     - Port 5000 is commonly used for development (and was Flask's default).
    #     - You will access your API at http://127.0.0.1:5000.
    #     - If this port is already busy, you can change it to 8000, 8080, etc.
    # 
    #   reload=True (Fourth Argument):
    #     - This is the "Live Update" switch (Development Mode only!).
    #     - When set to True, Uvicorn monitors all Python files in the project.
    #     - If you make a change and save a file, Uvicorn will automatically 
    #       restart the server to apply your changes.
    #     - This saves you from manually killing and restarting the server 
    #       every time you change your code.
    #     - WARNING: This should NEVER be set to True in a production environment.
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)