An API (Application Programming Interface) is like a digital waiter in a restaurant. The user orders a prediction by sending house data, the waiter takes it to the kitchen (our trained model), and then brings back the house price prediction. We will use Flask, which is a lightweight framework to build web servers in Python




The Super Important Secret (Scope):
This line of code is NOT inside a function. It is written at the top level of your file.
This means when your Flask server boots up, it runs this line ONLY ONCE. It loads the brain into RAM, and the brain sits there patiently, waiting for hours or days, until a user knocks on the door to ask for a prediction. You only pay the "loading cost" (0.01 seconds) one single time

