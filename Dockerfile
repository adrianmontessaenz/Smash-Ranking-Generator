# Use the official Python image as the base image
FROM python:3.11-slim

# Set environment variables to prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    python3-tk \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install virtualenv
RUN pip install --no-cache-dir --upgrade pip

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir gql requests pandas openpyxl flask requests_toolbelt customtkinter

# Expose port 8000 for development (if running a web server, for example)
EXPOSE 8000

# # Start the Flask application in development mode
# CMD ["flask", "run", "--host=0.0.0.0", "--port=8000"]

CMD [ "bash" ]
