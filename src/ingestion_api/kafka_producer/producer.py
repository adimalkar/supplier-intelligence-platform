import logging
from typing import Any
from confluent_kafka import Producer
from src.common.kafka.config import get_producer_config
from src.common.kafka.serializers import serialize_json

logger = logging.getLogger(__name__)

class KafkaProducerWrapper:
    def __init__(self, client_id: str = "ingestion-api"):
        self.producer = Producer(get_producer_config(client_id=client_id))

    def _delivery_callback(self, err, msg):
        if err:
            logger.error(f"Message failed delivery: {err}")
        else:
            logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")

    def produce_message(self, topic: str, key: str, value: dict[str, Any]):
        try:
            serialized_value = serialize_json(value)
            self.producer.produce(
                topic=topic,
                key=key.encode('utf-8') if key else None,
                value=serialized_value,
                callback=self._delivery_callback
            )
            self.producer.poll(0)
        except Exception as e:
            logger.error(f"Failed to produce message to {topic}: {e}")

    def flush(self):
        self.producer.flush()

producer = KafkaProducerWrapper()
