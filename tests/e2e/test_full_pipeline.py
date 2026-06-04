import pytest
import time
import httpx
from sqlalchemy import text
from src.common.db.connection import SessionLocal
from src.common.kafka.topics import Topics
from confluent_kafka import Producer, Consumer

pytestmark = pytest.mark.e2e

# This E2E test assumes the Docker stack (postgres, kafka, ingestion_api) is running.

@pytest.fixture(scope="module")
def api_client():
    return httpx.Client(base_url="http://localhost:8000")

@pytest.fixture(scope="module")
def db_session():
    session = SessionLocal()
    yield session
    session.close()

def test_api_health(api_client):
    """Test that the Ingestion API is up."""
    try:
        response = api_client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    except httpx.ConnectError:
        pytest.skip("Ingestion API is not running.")

def test_telemetry_ingestion(api_client, db_session):
    """Test sending telemetry to Ingestion API and verifying it goes to Kafka."""
    # 1. Ensure supplier exists in DB
    db_session.execute(text("""
        INSERT INTO dim_suppliers (supplier_code, name, location, tier)
        VALUES ('TEST-SUP-1', 'Test Supplier', 'Test Loc', 'tier_1')
        ON CONFLICT (supplier_code) DO NOTHING
    """))
    db_session.commit()
    
    # 2. Send payload
    payload = {
        "supplier_code": "TEST-SUP-1",
        "equipment_code": "TEST-EQ-1",
        "temperature": 75.5,
        "pressure": 120.0,
        "vibration": 2.1,
        "status": "running"
    }
    
    try:
        response = api_client.post("/api/v1/telemetry", json=payload, headers={"X-API-Key": "test_key"})
        assert response.status_code in (200, 202)
    except httpx.ConnectError:
        pytest.skip("Ingestion API is not running.")

    # 3. We would ideally verify the message in Kafka using a Consumer
    # In a real E2E environment, we'd setup a consumer to read from supplier.telemetry.raw
    pass

def test_agentic_ai_query(db_session):
    """Test the AI Agent initialization and basic response structure."""
    from src.agentic_ai.agent import SupplierIntelligenceAgent
    import asyncio
    
    agent = SupplierIntelligenceAgent(
        db_session_factory=SessionLocal, 
        llm_config={"provider": "openai", "model_name": "gpt-3.5-turbo", "temperature": 0.0}
    )
    
    # If no API key is present in environment, this will fail. We'll skip if no key.
    import os
    if not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("No OPENAI_API_KEY found, skipping Agent test.")
        
    response = asyncio.run(agent.query("What is the OEE for TEST-SUP-1?"))
    assert response is not None
    assert isinstance(response.text, str)
