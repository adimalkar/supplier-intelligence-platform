# System Architecture

The Supplier Intelligence Platform is a microservices-based system designed to collect, process, and analyze manufacturing telemetry and quality data in real-time.

## Components

1. **Edge Simulator**: Simulates factory equipment sending telemetry via gRPC.
2. **Ingestion API**: FastAPI service that receives telemetry and publishes to Kafka.
3. **Kafka Cluster**: Message broker that decouple ingestion from processing.
4. **Data Pipeline (Airflow)**: Consumes Kafka topics, transforms data, runs Computer Vision inference, and stores results in PostgreSQL/TimescaleDB.
5. **Computer Vision Module**: YOLOv8-based defect detection model.
6. **Agentic AI**: LangChain-powered AI assistant for root cause analysis and querying.
7. **Dashboard**: Streamlit app for real-time visualization.

## Data Flow
- `Edge -> Ingestion API -> Kafka -> Airflow -> PostgreSQL/TimescaleDB -> Dashboard`
