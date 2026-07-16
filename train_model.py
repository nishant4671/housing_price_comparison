# Import our classic tools






from sklearn.datasets import fetch_california_housing
import pandas as pd

# fetch_california_housing: The truck that brings the data from the internet.

# pandas as pd: The spreadsheet engine that organizes the data into neat rows and columns.

# Import our new production tools
from sklearn.preprocessing import StandardScaler

from sklearn.preprocessing import PolynomialFeatures

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
pipeline = Pipeline([('scaler', StandardScaler()), ('poly', PolynomialFeatures(degree=2, include_bias=False))])




# The DEEP Secret: Why include_bias=False is CRUCIAL
# The Rule: Never use include_bias=True when you are using StandardScaler or LinearRegression.

# Here is why:

# PolynomialFeatures is basically a robot that adds a column of 1s at the very beginning of your spreadsheet.

# LinearRegression is a robot that also adds a column of 1s automatically in its math (this is called the "Intercept" or b in Y = mX + b).

# If you let them both add a column of 1s, you get two identical columns of 1s right next to each other.

# When the math algorithm tries to figure out the best coefficients for these two identical columns, it gets confused. It asks: "Should I put the weight (θ) on Column A or Column B? They are exactly the same!"
# The math breaks down (technically, the matrix inversion fails or becomes unstable). This is called Multicollinearity.

# The Fix: include_bias=False tells the PolynomialFeatures robot: "Do NOT add the column of 1s. Leave that job for the LinearRegression robot to handle by itself."

# TL;DR: include_bias=False stops your model from having a math meltdown by preventing duplicate columns of 1s.





# PolynomialFeatures(degree=2, include_bias=False)
# This is the star of the show. Here is exactly what it does.

# The Problem:
# Your brain (Linear Regression) is a "straight line" thinker. It can only learn relationships that look like a straight line.
# Normal relationship: Price goes up steadily as rooms increase.
# Real relationship: Price skyrockets when rooms increase from 1 to 3, but barely moves when rooms increase from 7 to 9. It is a curved relationship.

# The Solution (PolynomialFeatures):
# This tool looks at your existing columns (like MedInc and HouseAge). It then builds brand new columns by doing math on the old ones.

# degree=2 (The Math Magic):
# It means: "For every single column, create a new column that is the square of it. Also, create new columns that are the multiplication of every pair of columns."

# Concrete Example:
# Imagine your original data has only 2 columns: X1 (Rooms) and X2 (Income).

# Original X1	Original X2
# 3	8
# 6	10
# When you apply PolynomialFeatures(degree=2), it turns your 2 columns into 5 new columns (for include_bias=True) or 4 new columns (for include_bias=False):

# X1 (Rooms)	X2 (Income)	X1² (Rooms Squared)	X1*X2 (Rooms × Income)	X2² (Income Squared)
# 3	8	9	24	64
# 6	10	36	60	100
# Now, when your model learns the math formula (ŷ = θ₀ + θ₁X1 + θ₂X2 + θ₃X1² + θ₄X1X2 + θ₅X2²), it can draw a curved line through your data because it has the X1² and X2² terms. This often makes the model much more accurate!






# ('poly', PolynomialFeatures(degree=2, include_bias=False))

# 'poly': The descriptive name for this step (short for "polynomial").

# PolynomialFeatures(...): This creates the actual tool that adds new columns to your data.




# # The Order of Operations (Crucial!)
# Look at the order in your list: scaler first, then poly.

# When you run pipeline.fit(X_train, y_train):

# Step 1 (scaler): It scales all your original numbers (e.g., turns MedInc from 0-15 into -2 to +2).

# Step 2 (poly): It takes these new, scaled numbers and creates the squared and multiplied columns from them.

# Why is this order genius?
# Imagine you have Population (0 to 50,000).

# If you do poly first, your new column Population² becomes 0 to 2.5 BILLION. That's a terrifyingly huge number that will cause math errors.

# By doing scaler first, Population is squashed down to -2 to +2. When poly squares it, the new column becomes 0 to 4. Small, stable, and mathematically beautiful. You scale first, then create the squared columns.









print("Step 2: Data loaded and Pipeline assembly line created!")

