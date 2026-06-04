FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for OpenCV and other CV packages
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Assuming requirements are passed or installed via pip
COPY pyproject.toml .
RUN pip install --no-cache-dir .[cv]

COPY . .

CMD ["python", "-m", "src.cv_module.train"]
