from flask import Flask, request, jsonify
# you are walking into the Flask library and grabbing exactly 3 specific tools:

# Flask (Capital F): This is the "Doorman Uniform". It is the main class you need to create your web application. Without this, you have no "front door."

# request (Lowercase r): This is the "Mailbox". When a user on the internet knocks on your door and hands you a letter (containing house details like rooms and income), request is the object that holds that letter so you can read it.

# jsonify (Lowercase j): This is the "Fancy Envelope Maker". Your model spits out a number (like 4.5). The internet doesn't speak raw numbers; it speaks JSON (which is just a standardized text format). jsonify wraps your number in a fancy JSON envelope so the user's browser can understand it.






import joblib
import pandas as pd

print("1. API tools imported!") # Run check

# Create our Flask web application server instance
app = Flask(__name__)


# this is the creation of the Doorman.

# app: This is your server instance. It's the actual "reception desk" that will listen for knocks on the door.

# Flask(...): You are calling the Flask class to build a brand new web application.

# __name__ (The Magic Variable): This is a special built-in Python variable. In plain English, it just means "this current file right here".

# When Python runs this script, __name__ is automatically set to "__main__".

# By passing it to Flask, you are telling Flask: "Hey, the boss of this server is this exact file (app.py). Look here to find the routes (the doorbells)."

# Ignore the weird underscores. Just know it's the required magic words to make Flask work.

# Load our frozen machine learning brain back into memory
model = joblib.load('house_model.joblib')

# joblib.load(): The unfreezer. It opens the file, reads the bytes, and reconstructs the exact Python object you saved earlier.

# 'house_model.joblib': The file path. Since you didn't specify a folder, Python looks in the current directory (the same folder where app.py is saved).

# model = ...: You are storing the revived brain back into a variable called model, exactly as it was in the training script.


print("2. Trained model brain loaded into the API server!") # Run check








# Tell Flask to listen for POST requests at the URL path '/predict'
# ===== YOUR CODE HERE =====
@app.route('/predict', methods=['POST'])

# The Decorator: @app.route('/predict', methods=['POST'])
# This is the "Doorbell Installation".

# @app.route(...): This is a Python "Decorator." In plain English, it is a special sticker that says: "Hey Flask, the function right below me is special. When someone visits this specific web address, run this function."

# '/predict': This is the specific door (the URL path). If your server is running at http://127.0.0.1:5000, this makes the full address http://127.0.0.1:5000/predict.

# methods=['POST']: This is the "Way to knock."

# GET is like visiting a webpage (you go to Google.com and look at the search bar).

# POST is like filling out a form and hitting "Submit" (you are sending data to the server). You force POST here because users must send the house details to you. If someone just types the URL into a browser (a GET request), Flask will automatically throw a 405 "Method Not Allowed" error. This is a security feature to protect your brain.







def predict_house_price():
#     The Function: def predict_house_price():
# This is the "Receptionist" who answers the door when the doorbell rings.

# You could name it anything (my_function, do_stuff), but predict_house_price is perfect because it tells you exactly what it does.

# Everything indented inside this function is the "script" the receptionist follows when a visitor arrives.



    print("3. Someone is asking for a prediction!") # Run check
    
    # 1. Grab the incoming JSON data sent to our digital waiter
    data = request.json

#     Line 2: data = request.json
# This is the "Reading the Letter" step.

# request: The Flask "mailbox" we imported earlier.

# .json: This grabs the raw JSON data that the user sent in their POST request and converts it into a Python Dictionary (a key-value pair object).

# For example: If a user sends {"MedInc": 8.3, "HouseAge": 41, "AveRooms": 6.9}, the data variable becomes a Python dictionary: {'MedInc': 8.3, 'HouseAge': 41, 'AveRooms': 6.9}.
    
#     # 2. Turn that data into a single row inside a Pandas DataFrame spreadsheet
    input_data = pd.DataFrame([data])
    



#     Line 3: input_data = pd.DataFrame([data])
# This is the "Translator" step. This is extremely important, so read carefully.

# pd.DataFrame(...): You are telling Pandas to build a spreadsheet (a DataFrame).

# [data] (The Square Brackets): This is the secret sauce.

# data is a dictionary: {'MedInc': 8.3, 'HouseAge': 41}.

# If you wrote pd.DataFrame(data), Pandas would get confused and treat the dictionary keys (MedInc, HouseAge) as row names, not column names. It would break.

# By wrapping it in square brackets [data], you are telling Pandas: "Hey, treat this entire dictionary as a SINGLE ROW of data."

# This builds a beautiful 1-row table where the column names are MedInc, HouseAge, and the value in that row is 8.3, 41





    # 3. Hand the spreadsheet to our brain to get the prediction
    prediction = model.predict(input_data)[0]
    


#     prediction = model.predict(input_data)[0]
# This is the "Asking the Brain" step.

# model.predict(input_data): You hand the 1-row DataFrame to your frozen brain. The brain does the math (remembers the equation ŷ = θ₀ + θ₁X₁ + ...) and spits out a list/array of predictions.

# Why [0] at the end? Because model.predict() always returns a list (an array), even if you only ask for 1 prediction. If you sent 5 houses, it would return 5 predictions. Since you sent 1 house, it returns a list with exactly 1 number inside (e.g., [4.526]). You put [0] at the end to grab the first and only number out of that list, so prediction becomes just the raw number 4.526.




    # 4. Send the calculated house price back to the user as JSON
    return jsonify({'predicted_price_in_hundred_thousands': float(prediction)})

# return jsonify({'predicted_price_in_hundred_thousands': float(prediction)})
# This is the "Sending the Reply" step.

# return: This sends the response back to the user who knocked on the door.

# jsonify(...): This wraps your reply in a fancy JSON envelope so the internet can read it.

# {'predicted_price_in_hundred_thousands': float(prediction)}:

# You are creating a brand new Python dictionary.

# The key is a string: 'predicted_price_in_hundred_thousands' (telling the user what this number means).

# The value is float(prediction). Your prediction might be a special numpy.float64 type (which is hard for the internet to read). Wrapping it in float() converts it to a standard Python decimal number that jsonify loves.

# What the user will see in their browser/terminal:

# json
# {"predicted_price_in_hundred_thousands": 4.526}
# (Meaning: the house is worth about $452,600)





# This keeps our web server running constantly so it can listen for visitors
if __name__ == '__main__':
    print("4. Launching the Flask server now...")
    app.run(port=5000)



# if __name__ == '__main__'::

# Remember how we passed __name__ to Flask earlier? Here is the magic.

# When you run python app.py directly, Python sets the special __name__ variable to "__main__".

# This if statement checks: "Is this file being run directly, or is it being imported as a module into another file?"

# If it is run directly (which it is), it runs the code inside.

# Why is this important? If someone else tried to import functions from your app.py into their script, this if block would NOT run, preventing your server from auto-starting and crashing their script. It's a safety feature.

# app.run(port=5000):

# This is the "Turn the Key in the Ignition".

# It starts the Flask development server. Your terminal will "hang" (blinking cursor). That means your server is alive and listening.

# port=5000: This is the specific "door number" on your computer. Your computer has 65,535 ports. Port 5000 is the standard Flask port. If you get an error saying Address already in use, it means you have another Flask app running. Change it to port=5001 or close the other terminal.

