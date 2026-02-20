"""
Kafka producer with retry and error handling.
"""
import json
import asyncio
from typing import Dict, Any, Optional
from kafka import KafkaProducer
from kafka.errors import KafkaError
import time

from config.settings import settings
from core.logging import get_logger
from core.exceptions import KafkaError as AppKafkaError

logger = get_logger("kafka_producer")


class KafkaProducerService:
    """Reliable Kafka producer with retry logic."""
    
    def __init__(self):
        self.producer: Optional[KafkaProducer] = None
        self._lock = asyncio.Lock()
    
    def _create_producer(self) -> KafkaProducer:
        """Create Kafka producer instance."""
        return KafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS.split(","),
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            acks="all",  # Wait for all replicas
            retries=settings.KAFKA_MAX_RETRIES,
            max_in_flight_requests_per_connection=1,  # Ensure ordering
            enable_idempotence=True,  # Prevent duplicates
            compression_type="gzip",
        )
    
    async def get_producer(self) -> KafkaProducer:
        """Get or create producer instance."""
        if self.producer is None:
            async with self._lock:
                if self.producer is None:
                    try:
                        self.producer = self._create_producer()
                        logger.info("Kafka producer created")
                    except Exception as e:
                        logger.error(f"Failed to create Kafka producer: {e}")
                        raise AppKafkaError(f"Failed to create producer: {e}")
        return self.producer
    
    async def publish(
        self,
        topic: str,
        value: Dict[str, Any],
        key: Optional[str] = None,
        retry: bool = True
    ) -> bool:
        """Publish message to Kafka topic."""
        try:
            producer = await self.get_producer()
            
            future = producer.send(
                topic=topic,
                value=value,
                key=key,
            )
            
            # Wait for delivery
            record_metadata = future.get(timeout=10)
            
            logger.info(
                f"Message published to {topic}",
                extra={
                    "extra_fields": {
                        "topic": topic,
                        "partition": record_metadata.partition,
                        "offset": record_metadata.offset,
                    }
                }
            )
            
            return True
            
        except KafkaError as e:
            logger.error(f"Kafka publish error: {e}")
            if retry and settings.KAFKA_MAX_RETRIES > 0:
                await asyncio.sleep(settings.KAFKA_RETRY_DELAY)
                return await self.publish(topic, value, key, retry=False)
            raise AppKafkaError(f"Failed to publish message: {e}")
        except Exception as e:
            logger.error(f"Unexpected error publishing to Kafka: {e}", exc_info=True)
            raise AppKafkaError(f"Unexpected error: {e}")
    
    async def publish_recommendation(self, event: Dict[str, Any]) -> bool:
        """Publish recommendation event."""
        return await self.publish(
            topic=settings.KAFKA_TOPIC_RECOMMENDATIONS,
            value=event,
            key=event.get("user_id") or event.get("session_id"),
        )
    
    async def publish_event(self, event: Dict[str, Any]) -> bool:
        """Publish general fashion event."""
        return await self.publish(
            topic=settings.KAFKA_TOPIC_EVENTS,
            value=event,
            key=event.get("event_id"),
        )
    
    async def close(self) -> None:
        """Close producer connection."""
        if self.producer:
            self.producer.close()
            self.producer = None
            logger.info("Kafka producer closed")


# Global producer instance
kafka_producer = KafkaProducerService()
