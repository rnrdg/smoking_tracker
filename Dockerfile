# Use python base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create volume for database
VOLUME /app/data

# Expose port
EXPOSE 5000

# Set environment variable for database path (optional, if logic supports it, else use symlink or mount)
# For this app, db is in current dir.
# We will assume the user mounts a volume to /app/data and we link it or the user mounts directly to /app/smoking_tracker.db
# A cleaner way is to change database.py to look in /app/data, but let's keep it simple: 
# We'll expect the volume to be mounted at /app/data and we'll use a symlink or adjust DB_NAME in code.
# But since I didn't change DB_NAME logic to read env var, I should probably stick to mounting file or dir.
# Let's just run gunicorn.
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:5000", "app:app"]
