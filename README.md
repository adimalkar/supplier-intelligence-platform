# Supplier Intelligence Platform

A Real-Time Supplier Intelligence & Quality Monitoring Platform designed for Tesla's Electronics Supplier Industrialization team.

## Overview

This platform enables real-time production performance monitoring across global suppliers, providing insights into Quality, Capacity, and Equipment performance. It uses Agentic AI for root-cause analysis and Computer Vision for automated defect detection on the edge.

## Tech Stack
- **Ingestion**: FastAPI, gRPC, Apache Kafka
- **Pipeline & Quality**: Apache Airflow, Great Expectations
- **Database**: PostgreSQL (TimescaleDB)
- **Computer Vision**: Ultralytics YOLOv8, PyTorch
- **AI Assistant**: LangChain, OpenAI/Bedrock
- **Dashboard**: Streamlit, Plotly
- **Infrastructure**: Docker, GitHub Actions

## Documentation

- [System Architecture](docs/architecture.md)
- [Data Dictionary](docs/data-dictionary.md)
- [Edge Deployment Guide](docs/edge-deployment-guide.md)
- [API Reference](docs/api-reference.md)

## Prerequisites

- Docker and Docker Compose
- Python 3.10+
- GNU Make

## Quick Start

1. Install dependencies:
   ```bash
   make setup
   ```
2. Start the infrastructure (Postgres + Kafka):
   ```bash
   make infra-up
   ```
3. Run DB migrations and seed data:
   ```bash
   make db-migrate
   make db-seed
   ```
4. Start Airflow pipeline:
   ```bash
   make airflow-up
   ```
5. Run the Ingestion API and Dashboard:
   ```bash
   make api
   make dashboard
   ```
6. (Optional) Run the Edge Simulator to generate traffic:
   ```bash
   make simulator
   ```
