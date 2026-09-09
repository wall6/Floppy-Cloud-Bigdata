FROM python:3.11-slim

# Install Java (required by Spark)
RUN apt-get update && \
    apt-get install -y openjdk-21-jre-headless && \
    apt-get clean

# Install PySpark and pandas
RUN pip install --no-cache-dir pyspark==3.5.1 "pandas<3.0"

# Set working directory inside the container
WORKDIR /app

# Copy project files into the container
COPY . /app

# Default command when the container runs
CMD ["python", "process_sales.py"]
