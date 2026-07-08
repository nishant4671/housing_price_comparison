from sklearn.datasets import fetch_california_housing

# What it does: It goes into the sklearn toolbox, opens the datasets drawer, and pulls out only the specific function called fetch_california_housing.

# Why not just import sklearn? If you just imported the whole library, you would have to type sklearn.datasets.fetch_california_housing() every time. By using from...import, you save typing and make your code cleaner. You can now just type fetch_california_housing().

# What is this function? It is a built-in "data delivery truck." When you call it, it goes to a Stanford University server, downloads a CSV file containing 20,640 rows of housing data from the 1990 California census, and hands it to you in a neat Python object.



import pandas as pd

# What it does: Imports the Pandas library and gives it the nickname pd.

# Why the nickname? Typing pandas 50 times is annoying. pd is the universally agreed-upon shortcut. Every data scientist in the world does this.



print("1. Tools successfully imported!")


# What it does: Prints a message to your terminal.

# Why is this here? This is a "Progress Check". Because you are a beginner, the AI tutor wants you to see instant feedback. If your terminal prints this, you know your imports are working. If your code crashes before this prints, you know the problem is your installation (maybe Pandas or Sklearn didn't install right).

raw_data = fetch_california_housing(as_frame=True)
# This is the most important line. Let's break it into pieces:

# fetch_california_housing(): The function that downloads the data.

# as_frame=True: This is the magic keyword.

# If you set this to False (or leave it out), the function gives you the data as pure numbers (NumPy arrays). You wouldn't know what column is what—just a sea of numbers.

# By setting it to True, you are telling Sklearn: "Hey, give me this data as a beautiful Pandas DataFrame with proper column names!" This saves you about 5 lines of code.

# raw_data = ...: This stores everything into a variable called raw_data.

# What is raw_data exactly? It is a special Python object called a "Bunch". Imagine it as a magical backpack. Inside this backpack (raw_data), there are multiple pockets:

# Pocket 1 (.data): The actual numbers (the features like rooms, income).

# Pocket 2 (.target): The actual prices (what you want to predict).

# Pocket 3 (.feature_names): The labels for the columns (e.g., "MedInc", "HouseAge").

# Pocket 4 (.frame): The complete merged table (features + target) as one single DataFrame.


print("2. Raw data loaded successfully!")


df = raw_data.frame

# What it does: You are reaching into the raw_data backpack, opening the .frame pocket, and pulling out the fully combined Pandas DataFrame.

# Why raw_data.frame and not raw_data.data?

# raw_data.data only gives you the input features (the X's).

# raw_data.target only gives you the prices (the y's).

# raw_data.frame gives you BOTH side-by-side in one beautiful spreadsheet. This is the easiest way to inspect the data with your own eyes.

print("\n--- FIRST 5 ROWS OF DATA ---")
print(df.head())



# print("\n--- FIRST 5 ROWS OF DATA ---"): Prints a fancy header line. The \n means "start a new line" so there is an empty line above it for readability.

# print(df.head()):

# What is .head()? A Pandas command that shows the first 5 rows of your DataFrame.

# Why 5? Because that's the default. It's enough to see the column names and sample data without overwhelming your terminal with 20,000 rows.


# Separate the clues (X) from the final answer we want to guess (y)
# We drop 'MedHouseVal' from X because the brain shouldn't see the answer while studying!
X = df.drop(columns=['MedHouseVal'])
y = df['MedHouseVal']

print("\n3. Data successfully split into Features (X) and Target (y)!")




from sklearn.linear_model import LinearRegression

# Create a blank, untrained model brain
model = LinearRegression()

# Tell the brain to look at the clues and learn the patterns
# ===== YOUR CODE HERE =====
# Type exactly: model.fit(X, y)


print("4. Brain successfully trained on the data!")


import joblib

# Save the trained brain into a file named 'house_model.joblib'
# ===== YOUR CODE HERE =====
joblib.dump(model, 'house_model.joblib')


print("5. Model brain frozen and saved to disk safely!")