from typing import Any
import json
from airflow.models import BaseOperator
from confluent_kafka import Consumer, KafkaError

class KafkaBatchConsumerOperator(BaseOperator):
    """Consume N messages from a Kafka topic and return them as a list of dicts."""
    
    def __init__(
        self,
        *,
        topic: str,
        kafka_conn_id: str = "kafka_default",
        batch_size: int = 100,
        timeout: float = 5.0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.topic = topic
        self.kafka_conn_id = kafka_conn_id
        self.batch_size = batch_size
        self.timeout = timeout

    def execute(self, context: Any) -> list[dict[str, Any]]:
        # For this project, we assume Kafka is at kafka:9092.
        conf = {
            'bootstrap.servers': 'kafka:9092',
            'group.id': 'airflow_pipeline_group',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False
        }
        
        consumer = Consumer(conf)
        consumer.subscribe([self.topic])
        
        messages = []
        try:
            for _ in range(self.batch_size):
                msg = consumer.poll(self.timeout)
                if msg is None:
                    break
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        raise Exception(msg.error())
                
                try:
                    val = json.loads(msg.value().decode('utf-8'))
                    messages.append(val)
                except Exception as e:
                    self.log.error(f"Failed to decode message: {e}")
                    # Dead-letter queue logic would go here
            if messages:
                consumer.commit(asynchronous=False)
        finally:
            consumer.close()
            
        self.log.info(f"Consumed {len(messages)} messages from {self.topic}")
        return messages
