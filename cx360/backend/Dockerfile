# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
# This assumes requirements.txt is in the root of the build context (./backend)
COPY requirements.txt .

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code from the build context (./backend) to the working directory /app
COPY . .

# Command to run the application
# main:app refers to the 'app' instance in 'main.py'
# Uvicorn will look for main.py in the WORKDIR (/app)
# The imports like 'from cx360.backend...' might require PYTHONPATH adjustments if /app is not seen as the parent of a 'cx360' package.
# However, if all 'cx360.backend' code is directly in /app, the imports should be relative, e.g. 'from .database import ...'
# For this exercise, we assume the current structure works or will be adjusted if run.
# A common way to handle this if 'main.py' is indeed in /app and contains 'from cx360.backend...'
# is that the effective PYTHONPATH when running uvicorn needs to include the directory *above* 'cx360'.
# This Dockerfile setup implies that /app *is* the 'backend' part of 'cx360.backend'.
# If main.py is in /app, and it uses "from cx360.backend...", Python won't find "cx360".
# The solution is often to place the Dockerfile in the project root (cx360/), copy all relevant code (e.g. COPY backend /app/backend)
# and then run uvicorn cx360.backend.main:app.
# Given the constraint that Dockerfile is in cx360/backend:
# We will assume for now that the command should be uvicorn main:app and that imports are relative (which they are not currently).
# To make the current imports work with this Dockerfile and context:
# The app needs to be structured so that /app is the parent of cx360.
# Let's adjust copy:
# WORKDIR /app_root
# COPY . /app_root/cx360/backend/
# ENV PYTHONPATH=/app_root
# CMD ["uvicorn", "cx360.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Sticking to the provided example's simplicity and addressing potential import issues in comments for now:
# The example Dockerfile is simple and assumes 'main.py' is directly runnable.
# If 'main.py' uses absolute imports like 'from cx360.backend...', it implies 'main.py'
# is NOT part of 'cx360.backend' but rather a script that launches it.
# The current 'main.py' *is* part of 'cx360.backend'.

# Let's make the Dockerfile robust for the current project structure where imports are "from cx360.backend..."
# This means the "cx360" directory needs to be the root from Python's perspective.
# If build context is "./backend", we are *inside* "cx360/backend".
# We need to reconstruct the "cx360" part.

# Revised plan for Dockerfile content:
# 1. WORKDIR /code
# 2. COPY . /code/cx360/backend/  (this creates the cx360.backend structure)
# 3. COPY requirements.txt /code/cx360/backend/requirements.txt (or just rely on it being in '.')
#    Actually, requirements.txt should be copied to where pip can find it before installing.
#    Better:
#    WORKDIR /code
#    COPY requirements.txt .
#    RUN pip install ...
#    COPY . /code/cx360/backend/ (problem: requirements.txt also copied here, and . means all of backend)

# Simplest robust Dockerfile given context is cx360/backend and imports are cx360.backend.xxx:
# This means the Python interpreter must see a directory structure like:
# some_root_dir/
#   cx360/
#     backend/
#       main.py
#
# If WORKDIR is /app and we COPY . ., then /app *is* backend.
# We need to make /app/.. the effective python path root, or / (if cx360 is put in /)

# Let's use the structure from the example, and assume Uvicorn handles pathing or it's simpler than thought.
# The most common interpretation of `CMD ["uvicorn", "main:app", ...]` with `WORKDIR /app` and `COPY . .`
# is that `main.py` is at `/app/main.py`.
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# This copies the content of cx360/backend into /app
COPY . .

# If main.py is in /app, and it starts with "from cx360.backend...", this will fail.
# The application's own files use "from cx360.backend...".
# This implies the code expects to be run from a directory *containing* "cx360".
# To fix this for Docker, if context is './backend':
# We need to create a structure inside the image where 'cx360/backend' exists.
# Option: WORKDIR /app_code
# COPY . /app_code/cx360/backend
# ENV PYTHONPATH /app_code
# CMD ["uvicorn", "cx360.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
# This is the most correct way given the current Python import paths.

# Re-creating with this more robust structure:
WORKDIR /app_code
COPY requirements.txt /app_code/requirements.txt
RUN pip install --no-cache-dir -r /app_code/requirements.txt
COPY . /app_code/cx360/backend
ENV PYTHONPATH /app_code

# Now, uvicorn can find cx360.backend.main
CMD ["uvicorn", "cx360.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
