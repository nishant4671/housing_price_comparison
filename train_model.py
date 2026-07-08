from sklearn.datasets import fetch_california_housing

# What it does: It goes into the sklearn toolbox, opens the datasets drawer, and pulls out only the specific function called fetch_california_housing.

# Why not just import sklearn? If you just imported the whole library, you would have to type sklearn.datasets.fetch_california_housing() every time. By using from...import, you save typing and make your code cleaner. You can now just type fetch_california_housing().

# What is this function? It is a built-in "data delivery truck." When you call it, it goes to a Stanford University server, downloads a CSV file containing 20,640 rows of housing data from the 1990 California census, and hands it to you in a neat Python object.



import pandas as pd

print("1. Tools successfully imported!")

raw_data = fetch_california_housing(as_frame=True)
print("2. Raw data loaded successfully!")

df = raw_data.frame

print("\n--- FIRST 5 ROWS OF DATA ---")
print(df.head())

