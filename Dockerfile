# Step 1: Use a slim Python image as our build engine
FROM python:3.11-slim AS builder

WORKDIR /app

# Install compilation tools if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment inside the container to keep it clean
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install dependencies first (this utilizes Docker's cache speed!)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Step 2: Create the final lightweight run image
FROM python:3.11-slim AS runner

WORKDIR /app

# Copy our isolated virtual environment from the builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy our app code and trained model brain
COPY app.py .
COPY house_model.joblib .

# Expose port 5000 for our API
EXPOSE 5000

# Tell Docker to run our server using uvicorn when the container starts
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]