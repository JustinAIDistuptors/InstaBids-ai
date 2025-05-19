# Use Python 3.10 image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install PostgreSQL client (for migrations or direct psql access if needed within container)
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
# This layer is cached if requirements.txt doesn't change
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code
# Copying src/instabids into the app directory under src/instabids
COPY ./src/instabids /app/src/instabids
# Copying api (which is at src/instabids/api) into the app directory under src/instabids/api
# This assumes your main.py is at src/instabids/api/main.py relative to the WORKDIR /app
# If api is a peer to src, then the COPY ./api /app/api line and uvicorn src.instabids.api.main:app makes sense
# Let's assume your structure has src/instabids/api where main.py lives.
# The docker-compose.yml mounts ./src/instabids:/app/src/instabids, so the app code is available.
# This COPY here is more for standalone Docker image builds.
# For consistency with docker-compose.yml which runs uvicorn src.instabids.api.main:app
# we should ensure that path resolves.

# The following COPY command assumes 'api' is a top-level directory, 
# but your FastAPI app lives in 'src/instabids/api'.
# Let's adjust the COPY and CMD to be consistent with 'src/instabids/api/main.py'
COPY . /app 
# This copies everything from the build context to /app. 
# A .dockerignore file would be useful to exclude .git, .vscode, etc.

# Add a non-root user and change ownership
# Running as non-root is a good security practice
RUN adduser --disabled-password --gecos "" instabids && \
    chown -R instabids:instabids /app

# Switch to non-root user
USER instabids

# Expose the port the app runs on
EXPOSE 8000

# Run using uvicorn, referencing the main.py from src.instabids.api
CMD ["uvicorn", "src.instabids.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
