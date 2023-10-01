# Use an official Python runtime as the parent image
FROM python:3.10.12-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the libraries from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8501 for Streamlit and 8888 for Jupyter
EXPOSE 8501 8888

# Command to run the startup script
CMD ["./start.sh"]