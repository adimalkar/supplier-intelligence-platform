FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (OpenCV requires libgl1 and libglib2.0)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY pyproject.toml .
# We just need to install the dependencies. If we use pip install ., it will install the package.
RUN pip install --no-cache-dir .

# Copy source code
COPY src/ src/

# Set Python path
ENV PYTHONPATH=/app

# Default command to run
ENTRYPOINT ["python", "-m", "src.edge_simulator.main"]
CMD ["--suppliers", "PREC_MOTORS", "--speed", "1.0"]
