# Use a stable Python base image
FROM python:3.11-alpine

# Set the working directory in the container
WORKDIR /app

# Install required system dependencies
RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev sqlite sqlite-dev

# Install required Python dependencies
RUN pip install --no-cache-dir flask flask-sqlalchemy pyyaml

# Copy the Flask application code into the container
COPY . .

# Expose the port that the Flask server will be running on
EXPOSE 5000

# Start the Flask server
CMD ["python", "webserver.py"]
