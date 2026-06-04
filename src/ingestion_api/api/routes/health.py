from fastapi import APIRouter
from src.common.db.connection import check_db_health
from src.common.kafka.config import check_kafka_health

router = APIRouter()

@router.get("/health")
def get_health():
    db_health = check_db_health()
    kafka_health = check_kafka_health()

    status = "ok" if db_health["status"] == "healthy" and kafka_health["status"] == "healthy" else "error"
    return {
        "status": status,
        "database": db_health,
        "kafka": kafka_health,
    }
