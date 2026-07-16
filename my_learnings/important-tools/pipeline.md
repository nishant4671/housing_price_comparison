2. from sklearn.pipeline import Pipeline
This is the "Assembly Line" or the "Production Conveyor Belt".

The Problem (The Messy Script):
Right now, your train_model.py script does things in a messy order:

Load data

Split data

Scale the Training data (using StandardScaler)

Scale the Test data

Train the model

Save it

If you ever change the order, or add a new step (like "remove outliers"), you have to manually rewrite everything. It's like cooking without a recipe—you can do it, but you'll forget a step when you're tired.

The Solution (Pipeline):
A Pipeline is a single object that chains all your preprocessing steps (like StandardScaler) and your model (like LinearRegression) into one neat, bulletproof conveyor belt.

The Analogy (Car Factory):
Imagine building a car:

Station 1: Weld the frame.

Station 2: Paint it.

Station 3: Install the engine.

Station 4: Test drive.

Instead of doing these 4 steps manually every time, you build a conveyor belt (Pipeline) that does all 4 steps automatically, in the exact right order, every single time.

Your Project's Pipeline:
Station 1: Scale the data (StandardScaler).
Station 2: Train the model (LinearRegression).

