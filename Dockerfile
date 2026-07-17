# =============================================================================
# COMMENTARY ON THE DOCKERFILE BELOW
# =============================================================================
# This is a "Multi-Stage" Dockerfile.
# Dockerfiles are recipes that tell Docker how to build a portable, isolated
# environment (a container) for your application to run in.
#
# "Multi-Stage" means it has two separate parts (stages):
#   - Stage 1 (Builder): The "kitchen" where we compile and prepare everything.
#   - Stage 2 (Runner): The "dining room" where we actually serve the application.
# The final image (Runner) is kept tiny because it only contains the final
# runtime files, not the bulky compilers and temporary files from Stage 1.
# =============================================================================


# -----------------------------------------------------------------------------
# SECTION 1: THE BUILDER STAGE (The "Preparation Kitchen")
# -----------------------------------------------------------------------------

# Step 1: Use a slim Python image as our build engine
#
# FROM python:3.11-slim AS builder
#
# WHAT IT DOES:
# - "FROM" tells Docker which base image to start from.
# - "python:3.11-slim": This is a lightweight official Python image from Docker Hub.
#   - "python" is the image name.
#   - "3.11-slim" is the tag. "slim" means it contains only the bare minimum
#     to run Python (no extra tools or compilers). It's around ~120MB instead of
#     the full ~900MB image. This keeps our final container small.
# - "AS builder": This gives a NAME to this first stage. We will refer to this
#   name later when we copy files from this stage into the final runner stage.
FROM python:3.11-slim AS builder

# WORKDIR /app
#
# WHAT IT DOES:
# - "WORKDIR" sets the current working directory inside the container.
# - If the folder doesn't exist, Docker creates it automatically.
# - All subsequent commands (RUN, COPY, CMD) will run from this location.
# - We set it to "/app" because that is the standard convention for application
#   code inside containers. It keeps things organized.
WORKDIR /app

# Install compilation tools if needed
#
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     && rm -rf /var/lib/apt/lists/*
#
# WHAT IT DOES:
# - "RUN" executes a shell command inside the container.
# - "apt-get update": Updates the list of available packages (like refreshing
#   the app store catalog).
# - "apt-get install -y": Installs a package. "-y" automatically says "yes"
#   to all prompts (non-interactive mode).
# - "build-essential": This is a meta-package on Ubuntu/Debian that installs
#   essential compilers (gcc, g++, make) and standard libraries.
#   - Why do we need this? Some Python libraries (especially scikit-learn and
#     numpy) have underlying C/C++ code that needs to be compiled during
#     installation. Without a compiler, `pip install` fails.
# - "--no-install-recommends": This flag tells apt to ONLY install the
#   absolute core packages, not any "recommended" extras. This keeps the image small.
# - "&& rm -rf /var/lib/apt/lists/*": This is a CLEANUP trick.
#   - After installing packages, the apt cache (list of packages) remains on disk.
#   - We delete it IMMEDIATELY after installation. This removes ~20MB of
#     unnecessary files and prevents the final image from bloating.
#   - This is the #1 best practice for writing Dockerfiles.
# 
# CRITICAL NOTE: The "--no-install-recommends" and "rm -rf" are essential to
# keep the builder stage as small as possible, even though it contains compilers.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment inside the container to keep it clean
#
# RUN python -m venv /opt/venv
#
# WHAT IT DOES:
# - "python -m venv": Calls Python's built-in virtual environment module.
# - "/opt/venv": The path where the virtual environment will be created.
#   - "/opt" is a standard Linux directory for optional/third-party software.
#   - We are creating the venv outside the "/app" folder to keep our
#     application code separate from the system dependencies.
# - Why a virtual environment INSIDE a container? Containers are already
#   isolated, but Python still installs packages globally inside the container
#   by default. Using a venv gives us an extra layer of isolation and ensures
#   we are not accidentally cluttering the system Python. It also makes it
#   easier to copy JUST the compiled packages to the final stage.
RUN python -m venv /opt/venv

# ENV PATH="/opt/venv/bin:$PATH"
#
# WHAT IT DOES:
# - "ENV" sets an environment variable inside the container.
# - "PATH="/opt/venv/bin:$PATH"" updates the system PATH.
#   - "/opt/venv/bin" is the folder where the virtual environment's `pip` and
#     `python` executables live.
#   - ":$PATH" appends the rest of the existing PATH.
# - By doing this, every subsequent "RUN pip install" or "RUN python" command
#   automatically uses the virtual environment instead of the system Python.
# - This means we don't have to type "/opt/venv/bin/pip" every time.
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install dependencies first (this utilizes Docker's cache speed!)
#
# COPY requirements.txt .
#
# WHAT IT DOES:
# - "COPY" copies a file from your local computer (the build context) into
#   the container's filesystem.
# - "requirements.txt" is the source file on your computer.
# - "." is the destination inside the container (the current WORKDIR, which is /app).
# - This copies your dependency list into the container.
#
# WHY DO WE COPY requirements.txt BEFORE copying the rest of the code?
# - This is a MASTERFUL Docker caching trick.
# - Docker caches the result of each "RUN" command.
# - If you copy ALL your code first, and then run `pip install`, changing
#   ANY file in your project (like app.py) will break Docker's cache for
#   the entire `pip install` step, forcing it to re-install everything
#   (which takes 5 minutes).
# - By copying requirements.txt FIRST, Docker sees: "The requirements.txt
#   hasn't changed, so I will reuse the cached pip install layer."
# - This saves you 5 minutes of wait time when you are just tweaking your app.py code.
COPY requirements.txt .

# RUN pip install --no-cache-dir -r requirements.txt
#
# WHAT IT DOES:
# - "pip install": The package installer.
# - "--no-cache-dir": Tells pip not to store a local cache of downloaded
#   package wheels. This saves disk space inside the container.
# - "-r requirements.txt": Tells pip to install all the packages listed in
#   the requirements.txt file (FastAPI, Pandas, Scikit-learn, Uvicorn, etc.).
# - The compilers we installed earlier (build-essential) are now used here
#   to compile scikit-learn and numpy from source (if no pre-built wheels exist
#   for the architecture).
# - All these packages are installed INSIDE the `/opt/venv` virtual environment.
RUN pip install --no-cache-dir -r requirements.txt


# -----------------------------------------------------------------------------
# SECTION 2: THE RUNNER STAGE (The "Serving Dining Room")
# -----------------------------------------------------------------------------

# Step 2: Create the final lightweight run image
#
# FROM python:3.11-slim AS runner
#
# WHAT IT DOES:
# - This starts a COMPLETELY NEW container image from scratch.
# - It does NOT inherit the bulky builder stage.
# - It pulls a fresh python:3.11-slim base image (again, the tiny 120MB version).
# - "AS runner" gives this second stage a name (optional, but good practice).
# - Why start fresh? We want to discard the massive compilers (build-essential)
#   and temporary files from the builder stage. The final runner image will be
#   tiny (~200MB) instead of massive (~1GB).
FROM python:3.11-slim AS runner

# WORKDIR /app
#
# WHAT IT DOES:
# - Sets the working directory to /app in this runner stage as well.
# - This is independent of the builder stage.
WORKDIR /app

# Copy our isolated virtual environment from the builder
#
# COPY --from=builder /opt/venv /opt/venv
#
# WHAT IT DOES:
# - This is the MAGIC of multi-stage builds.
# - "--from=builder" tells Docker: "Do not copy from the local computer.
#   Instead, copy from the FILESYSTEM of the PREVIOUS stage named 'builder'."
# - "/opt/venv" is the source path inside the builder stage.
# - "/opt/venv" is the destination path inside the current runner stage.
# - This copies the ENTIRE virtual environment (including Python, Pip, and
#   all your installed libraries like FastAPI, Pandas, Scikit-learn, etc.)
#   from the builder stage into the runner stage.
# - Because the runner starts fresh, it does NOT contain build-essential.
#   The /opt/venv folder contains the compiled C extensions, so they are
#   ready to run without needing the compilers at runtime.
COPY --from=builder /opt/venv /opt/venv

# ENV PATH="/opt/venv/bin:$PATH"
#
# WHAT IT DOES:
# - Just like in the builder stage, we set the PATH so that the virtual
#   environment's Python and Pip are the default executables used when
#   the container runs.
ENV PATH="/opt/venv/bin:$PATH"

# Copy our app code and trained model brain
#
# COPY app.py .
#
# WHAT IT DOES:
# - Copies your application code (app.py) from your local computer into the
#   container's WORKDIR (/app).
# - This contains your FastAPI endpoints, Pydantic models, and routing logic.
COPY app.py .

# COPY house_model.joblib .
#
# WHAT IT DOES:
# - Copies your pre-trained machine learning pipeline (the frozen brain)
#   from your local computer into the container's /app folder.
# - This file is critical. Without it, the API will crash on startup because
#   `joblib.load('house_model.joblib')` will fail.
# - We copy it here, after the requirements and code, so that if the model
#   changes frequently, we don't bust the cache for the dependency installation.
COPY house_model.joblib .

# Expose port 5000 for our API
#
# EXPOSE 5000
#
# WHAT IT DOES:
# - "EXPOSE" is purely DOCUMENTATION. It does NOT actually publish the port.
# - It tells the person reading the Dockerfile (and the Docker tooling) that
#   the application inside the container listens on port 5000.
# - When you run the container with `docker run -p 5000:5000`, the `-p` flag
#   actually maps the host port to the container port. EXPOSE just tells
#   you which port to map.
EXPOSE 5000

# Tell Docker to run our server using uvicorn when the container starts
#
# CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
#
# WHAT IT DOES:
# - "CMD" is the command that runs when the container starts.
# - Unlike "RUN" (which runs during the build phase), "CMD" runs at runtime.
# - ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]:
#   - "uvicorn": The ASGI web server we installed in the builder.
#   - "app:app": Points to your FastAPI instance (file: app.py, variable: app).
#   - "--host 0.0.0.0": Tells uvicorn to listen on ALL network interfaces
#     inside the container. This is CRITICAL because the container has its
#     own internal IP. If you set 127.0.0.1, it would only accept requests
#     from inside the container itself, and the outside world couldn't reach it.
#   - "--port 5000": Runs the server on port 5000 inside the container.
# - When you run `docker run` and map port 5000, this command starts your API.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]

# =============================================================================
# END OF DOCKERFILE
# =============================================================================
# HOW TO BUILD AND RUN THIS DOCKERFILE:
#
# 1. Build the image:
#    docker build -t house-price-api .
#    (This runs both stages and creates the final compressed image)
#
# 2. Run the container:
#    docker run -p 5000:5000 house-price-api
#    (Maps your computer's port 5000 to the container's port 5000)
#
# 3. Test it:
#    Open your browser to http://127.0.0.1:5000/docs
#
# WHY MULTI-STAGE?
# - Builder Image size (if you didn't use multi-stage): ~1.2 GB.
# - Final Runner Image size (with multi-stage): ~200 MB.
# - You saved ~1 GB by throwing away the compilers and temporary files.
# =============================================================================