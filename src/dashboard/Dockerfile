FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install .

COPY src/ src/

ENV PYTHONPATH=/app
EXPOSE 8501

CMD ["streamlit", "run", "src/dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
