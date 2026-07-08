from sklearn.datasets import fetch_california_housing
import pandas as pd

print("1. Tools successfully imported!")

raw_data = fetch_california_housing(as_frame=True)
print("2. Raw data loaded successfully!")

df = raw_data.frame

print("\n--- FIRST 5 ROWS OF DATA ---")
print(df.head())



if you get a red error, here are the 3 most likely culprits:

Network Error (SSL/Certificate): If your corporate internet blocks the download, it will fail. Tell your AI tutor: "I got an SSL network error loading the data." It will tell you to add ssl._create_default_https_context = ssl._create_unverified_context at the top.

ModuleNotFoundError: If it says ModuleNotFoundError: No module named 'sklearn', it means pip install scikit-learn didn't finish or you are running the script outside of your venv. Make sure your terminal prompt shows (venv) at the start.

NameError: If it says NameError: name 'pd' is not defined, it means you forgot to type import pandas as pd before using pd.DataFrame.

