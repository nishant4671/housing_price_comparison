# Import our classic tools
from sklearn.datasets import fetch_california_housing
import pandas as pd

# fetch_california_housing: The truck that brings the data from the internet.

# pandas as pd: The spreadsheet engine that organizes the data into neat rows and columns.

# Import our new production tools
from sklearn.preprocessing import StandardScaler

# from sklearn.preprocessing import StandardScaler
# This is the "Equalizer" or the "Fairness Officer".

# The Problem (The Scale Trap):
# Remember the math formula for Linear Regression?

# ŷ = θ₀ + θ₁(MedInc) + θ₂(HouseAge) + θ₃(AveRooms) + ...

# Here is the dirty secret: Linear Regression is biased toward bigger numbers.

# If MedInc ranges from 0 to 15 (small scale) and Population ranges from 0 to 50,000 (huge scale), the math algorithm will assume Population is 3,000 times more important—not because it actually matters more, but just because the numbers are bigger. The coefficients (θ) will shrink for Population and blow up for MedInc, making the math unstable.

# The Solution (StandardScaler):
# It forces every single column to have the exact same scale—a mean of 0 and a standard deviation of 1.

# The Math Formula (Z-Score Normalization):

# X_scaled = (X - μ) / σ

# Translation:

# X = Your original number (e.g., MedInc = 8.3).

# μ (Mu) = The average (mean) of all MedInc values in your dataset.

# σ (Sigma) = The standard deviation (how spread out the numbers are).

# X_scaled = The new, fair number.

# Concrete Example:
# Imagine two columns:

# Original MedInc	Original Population	Scaled MedInc	Scaled Population
# 8.3	322	+1.5	+0.2
# 3.5	1500	-0.8	+1.8
# The scaled numbers are now in a fair range (roughly -3 to +3). The model can now judge them purely on how useful they are for predicting price, not on the size of the number.

# Critical Rule (The "Fit" vs "Transform" secret):

# scaler.fit(X_train): Calculate μ and σ based only on the Training Set.

# scaler.transform(X_train): Apply that formula to the Training Set to scale it.

# scaler.transform(X_test): Apply the EXACT SAME μ and σ (calculated from the training set) to the Test Set.

# Why not re-calculate μ and σ for the Test Set? Because in the real world, you don't know the average income of future houses. You must treat the Test Set like "alien data" and use the rules you learned from training data.


# ===== YOUR CODE HERE =====
from sklearn.pipeline import Pipeline

# This is the "Assembly Line" or the "Production Conveyor Belt".

# The Problem (The Messy Script):
# Right now, your train_model.py script does things in a messy order:

# Load data

# Split data

# Scale the Training data (using StandardScaler)

# Scale the Test data

# Train the model

# Save it

# If you ever change the order, or add a new step (like "remove outliers"), you have to manually rewrite everything. It's like cooking without a recipe—you can do it, but you'll forget a step when you're tired.

# The Solution (Pipeline):
# A Pipeline is a single object that chains all your preprocessing steps (like StandardScaler) and your model (like LinearRegression) into one neat, bulletproof conveyor belt.

# The Analogy (Car Factory):
# Imagine building a car:

# Station 1: Weld the frame.

# Station 2: Paint it.

# Station 3: Install the engine.

# Station 4: Test drive.

# Instead of doing these 4 steps manually every time, you build a conveyor belt (Pipeline) that does all 4 steps automatically, in the exact right order, every single time.

# Your Project's Pipeline:
# Station 1: Scale the data (StandardScaler).
# Station 2: Train the model (LinearRegression).



print("Step 1: Upgraded tools imported successfully!")




# 1. Load the raw data
raw_data = fetch_california_housing(as_frame=True)
df = raw_data.frame

# 2. Split into clues (X) and answers (y)
X = df.drop(columns=['MedHouseVal'])
y = df['MedHouseVal']

# 3. Create the assembly line
# We name our first station 'scaler' and put StandardScaler inside it.
# ===== YOUR CODE HERE =====
pipeline = Pipeline([('scaler', StandardScaler())])


print("Step 2: Data loaded and Pipeline assembly line created!")

