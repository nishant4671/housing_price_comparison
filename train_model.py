# ====================================================================
# IMPORT SECTION: Bringing in our tools from the Python universe
# ====================================================================

# 1. fetch_california_housing: The "data delivery truck".
#    It connects to a Stanford server, downloads the 1990 California census data,
#    and hands it to us as a Python object.
from sklearn.datasets import fetch_california_housing

# 2. GridSearchCV: The "Hyperparameter Tuning Robot".
#    This is an intelligent, tireless robot that tests many different settings
#    (like alpha values) for your model, runs multiple training sessions, and tells
#    you which settings produce the lowest error. It automates the "trial and error" 
#    process completely.
from sklearn.model_selection import GridSearchCV

# 3. StandardScaler: The "Fairness Officer".
#    Forces all columns to have a mean of 0 and a standard deviation of 1.
#    This stops the model from unfairly favoring columns just because they have 
#    larger numbers (e.g., treating "Population" as more important than "Income").
from sklearn.preprocessing import StandardScaler

# 4. PolynomialFeatures: The "Feature Creator".
#    Looks at your existing columns (like "Rooms" and "Income") and mathematically
#    creates BRAND NEW columns: the squares (Rooms²), cubes, and multiplications 
#    (Rooms × Income). This allows your "straight-line" model to learn "curved" 
#    relationships in the data.
from sklearn.preprocessing import PolynomialFeatures

# 5. Ridge: The "Strict School Principal" (instead of LinearRegression).
#    This is a special version of Linear Regression that adds a penalty for 
#    overly complex math. If the model tries to make the coefficients (θ values) 
#    extremely huge to perfectly fit the training data, Ridge punishes it. 
#    This prevents "Overfitting" (memorizing the training data) and forces the 
#    model to learn general patterns that work on new, unseen houses.
from sklearn.linear_model import Ridge

# 6. Pipeline: The "Assembly Line Conveyor Belt".
#    Chains together multiple steps (Scaler -> Polynomials -> Ridge Model)
#    into one single, bulletproof object. It ensures the steps always happen 
#    in the exact right order, and it prevents data leakage (the #1 beginner mistake).
from sklearn.pipeline import Pipeline

# 7. pandas as pd: The "Spreadsheet Engine".
#    Takes messy raw data and organizes it into neat rows and columns 
#    (DataFrames) that are easy to inspect and manipulate.
import pandas as pd

# 8. joblib: The "Freezer/Unfreezer".
#    Saves your trained model from your computer's temporary RAM to your hard drive
#    as a permanent .joblib file. Later, your Flask API will use this to load
#    the brain back instantly without retraining.
import joblib

# --------------------------------------------------------------------
# RUN CHECK 1: Just a friendly "Hello" in the terminal so you know 
#              the imports worked and your code hasn't crashed yet.
# --------------------------------------------------------------------
print("1. All production tools imported!")


# ====================================================================
# DATA LOADING & SPLITTING SECTION
# ====================================================================

# Tell the delivery truck to go get the data. 
# as_frame=True means: "Bring the data back as a beautiful Pandas DataFrame 
# (with column names), not as a messy grid of anonymous numbers."
raw_data = fetch_california_housing(as_frame=True)

# raw_data is a "Bunch" object (think of it as a magical backpack).
# .frame is the pocket in that backpack that contains the FULL table 
# (all 8 feature columns + the 1 target price column) combined into one DataFrame.
df = raw_data.frame

# --- SEPARATE THE CLUES (X) FROM THE ANSWER (y) ---

# X = The "Clues" or "Input Features".
# We drop (remove) the 'MedHouseVal' column from the DataFrame.
# We are doing this because we want X to contain ONLY the information the model 
# is allowed to look at. The model must NOT see the price during training, 
# otherwise it would just memorize it and cheat on the exam.
# axis=1 means "drop a column" (axis=0 would drop a row).
X = df.drop(columns=['MedHouseVal'])

# y = The "Answer Key" or "Target Variable".
# We grab ONLY the 'MedHouseVal' column. This is a single column containing
# the actual, correct prices for every house in the dataset.
# The model's job is to learn how to guess these prices based on X.
y = df['MedHouseVal']

# --------------------------------------------------------------------
# RUN CHECK 2: Confirms the split happened and the data is ready.
# --------------------------------------------------------------------
print("2. Data split into X and y!")


# ====================================================================
# PIPELINE CONSTRUCTION: Building the 3-Station Assembly Line
# ====================================================================

# This creates the conveyor belt with exactly 3 stations.
# Data enters at Station 1, goes to Station 2, then Station 3.
pipeline = Pipeline([
    
    # ----- STATION 1: The Scaler -----
    # Name: 'scaler'. Tool: StandardScaler().
    # What it does: Takes the raw X data (which has columns with wildly different
    # scales, e.g., Income 0-15, Population 0-50,000). It crunches the numbers 
    # and spits out a new version of X where every column has a mean of 0 and a 
    # standard deviation of 1. The math is stable and fair here.
    ('scaler', StandardScaler()),
    
    # ----- STATION 2: The Polynomial Creator -----
    # Name: 'poly'. Tool: PolynomialFeatures(degree=2, include_bias=False).
    # degree=2: Means "Create squared terms and interaction terms". If you had 
    #           columns A and B, it creates A², B², and A*B. This lets the 
    #           model draw curved lines through the data.
    # include_bias=False: This is CRUCIAL. Without this, it adds a column of
    #                     all '1's. But Ridge (Station 3) also adds its own 
    #                     column of '1's automatically. Two identical columns 
    #                     of '1's would crash the math. So we turn the first 
    #                     one OFF here to prevent that duplication.
    ('poly', PolynomialFeatures(degree=2, include_bias=False)),
    
    # ----- STATION 3: The Ridge "Strict Principal" Model -----
    # Name: 'ridge'. Tool: Ridge().
    # Why Ridge instead of LinearRegression? Ridge adds a penalty. If the model
    # tries to make the weights (coefficients) super massive to overfit the data,
    # Ridge says "STOP!" and adds a mathematical "fine" (penalty) for big weights.
    # This forces the model to keep the weights small, which actually makes it 
    # work BETTER on brand new, unseen houses (generalization).
    ('ridge', Ridge())
])


# ====================================================================
# HYPERPARAMETER GRID DEFINITION
# ====================================================================

# This is the shopping list of different "Alpha" (penalty strength) values
# we want the GridSearch robot to test.
# 
# Alpha is the "strictness" knob for the Ridge model.
# - High Alpha (e.g., 100.0): Very strict. Keeps weights very small. 
#   Good if data is noisy or you have few rows.
# - Low Alpha (e.g., 0.1): Very relaxed. Almost like normal Linear Regression.
#   Good if data is clean and you have lots of rows.
#
# The double underscore '__' in 'ridge__alpha' is SPECIAL syntax for Pipeline.
# It means: "Hey GridSearch, go inside the step named 'ridge' and adjust its 
# parameter called 'alpha'." Without the double underscore, GridSearch wouldn't
# know which step to look at.
param_grid = {
    'ridge__alpha': [0.1, 1.0, 10.0, 100.0]
}


# ====================================================================
# GRID SEARCH SETUP: The Intelligent Robot
# ====================================================================

# GridSearchCV creates an intelligent robot that will:
# 1. Take your Pipeline.
# 2. Try ALL the alpha values in the param_grid.
# 3. For EACH alpha, it will do "Cross-Validation" (CV).
#
# cv=5 (5-Fold Cross-Validation):
#   This is extremely important. GridSearch does NOT just split the data 
#   once into training/test. Instead, it splits the data into 5 equal 
#   "folds" (like 5 boxes). It trains on 4 boxes and tests on 1 box. 
#   It rotates this 5 times, so every box gets tested once. 
#   It then averages the error over these 5 tests. This gives a MUCH more
#   reliable score than just splitting once.
#
# scoring='neg_mean_squared_error':
#   This is the "grading system". GridSearch calculates the Mean Squared Error
#   (how wrong the predictions are). In Scikit-learn, the convention is 
#   "higher is better". Since MSE is an error (lower is better), we use the 
#   NEGATIVE version. So -1000 is better than -5000. Don't worry about the 
#   negative sign; GridSearch just uses it to rank the options internally.
grid_search = GridSearchCV(pipeline, param_grid, cv=5, scoring='neg_mean_squared_error')

# --------------------------------------------------------------------
# RUN CHECK 3: Confirms the tools are built and ready to start the heavy work.
# --------------------------------------------------------------------
print("3. Pipeline and GridSearch ready. Training the brain now...")


# ====================================================================
# THE "TRAIN" COMMAND: Dropping the Nuclear Bomb of Processing
# ====================================================================

# IMPORTANT: Notice we pass in the FULL X and y here!
# We did NOT manually do train_test_split earlier.
# Why? GridSearchCV is incredibly smart. It will AUTOMATICALLY handle the 
# train/test splits internally using its Cross-Validation (cv=5) system.
# 
# What happens when you run this?
# 1. GridSearchCV takes X and y.
# 2. For alpha=0.1: It runs the pipeline (Scaler->Poly->Ridge) 5 times 
#    (training on 4/5 of the data, testing on 1/5), records the average error.
# 3. For alpha=1.0: Does the same 5-fold process.
# 4. For alpha=10.0: Does the same.
# 5. For alpha=100.0: Does the same.
# 6. After 20 separate training runs (4 alphas * 5 folds), it compares the 
#    average errors and selects the alpha with the LOWEST (most negative) MSE.
# 
# Wait, why not use X_train and X_test?
# If you manually split your data, GridSearch would still use Cross-Validation 
# INSIDE your X_train. Then you would test the final best model on your 
# manually held-out X_test. It's perfectly fine, but for simplicity, we just 
# pass the full X. GridSearch handles all the separation internally.
# ===== YOUR CODE HERE =====
grid_search.fit(X, y)

# --------------------------------------------------------------------
# RUN CHECK 4: Confirms the massive grid search finished successfully!
# --------------------------------------------------------------------
print("4. Brain successfully trained with optimal settings!")


# ====================================================================
# EXTRACTING THE GOLDEN MODEL
# ====================================================================

# After grid_search.fit() completes, the 'best_estimator_' attribute contains
# the exact Pipeline that performed the best across all cross-validation tests.
# 
# It contains:
# - The specific alpha value (e.g., 10.0) that gave the lowest error.
# - The Scaler that was fitted to the data.
# - The PolynomialFeatures that was created.
# - The Ridge model that was trained with that optimal alpha.
best_pipeline = grid_search.best_estimator_


# ====================================================================
# FREEZING THE PERFECT PIPELINE
# ====================================================================

# Now we take this best_pipeline (which is a combination of Scaler + Poly + Ridge)
# and we "freeze" it onto our hard drive.
# 
# Why save the whole pipeline instead of just the Ridge model?
# Because if you just save the Ridge model, you would have to manually re-scale
# your test data and manually create the polynomial columns every time you want
# to predict a new house. That is a massive hassle.
# By saving the entire Pipeline, it contains the SCALER's internal math (mean/std)
# and the POLY's column configuration. When you load it in Flask and type
# model.predict(), the pipeline automatically scales and creates polynomials for
# the new data using the exact same rules it learned during training.
# ===== YOUR CODE HERE =====
joblib.dump(best_pipeline, 'house_model.joblib')

# --------------------------------------------------------------------
# RUN CHECK 5: Mission Complete! The file 'house_model.joblib' now exists.
# --------------------------------------------------------------------
print("5. Upgraded production pipeline saved to disk!")




# This script is the "Professional Production Line": it loads the housing data, creates a 3-step assembly line (Scale → Create Polynomials → Ridge Model), uses an intelligent robot (GridSearchCV) to test 4 different alpha penalty strengths across 5 rounds of cross-validation to find the most accurate version, extracts the golden pipeline, and permanently freezes it to your hard drive as house_model.joblib—ready to be loaded into your Flask API for real-world predictions.