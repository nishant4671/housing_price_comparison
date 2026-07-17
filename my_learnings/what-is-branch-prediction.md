The Big Picture (What is Batch Prediction?)
Batch prediction allows the user to send multiple houses at once in a single API call. Instead of calling /predict 100 times separately (which creates 100 network round-trips), the user sends 100 houses in one JSON array, and your API predicts all of them in a single, ultra-fast swoop.

This is more efficient, faster, and cheaper (fewer network calls).

