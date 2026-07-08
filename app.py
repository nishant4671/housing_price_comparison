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


print("2. Trained model brain loaded into the API server!") # Run check