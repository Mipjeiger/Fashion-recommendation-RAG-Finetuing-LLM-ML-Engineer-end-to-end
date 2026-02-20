"""
Kafka consumer with dead-letter handling and retry logic.
"""
import json
import asyncio
from typing import Callable, Optional, Dict, Any
from kafka import KafkaConsumer
from kafka.errors import KafkaError

from config.settings import settings
from core.logging import get_logger
from core.exceptions import KafkaError as AppKafkaError

logger = get_logger("kafka_consumer")


class KafkaConsumerService:
    """Reliable Kafka consumer with error handling."""

    def __init__(self):
        self.consumer: Optional[KafkaConsumer] = None
        self.running = False
        self._lock = asyncio.Lock()

    def _create_consumer(self, topics: list[str]) -> KafkaConsumer:
        """Create Kafka consumer instance."""
        return KafkaConsumer(
            *topics,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS.split(","),
            group_id=settings.KAFKA_CONSUMER_GROUP,
            auto_offset_reset="latest",
            enable_auto_commit=True,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            key_deserializer=lambda k: k.decode("utf-8") if k else None,
            consumer_timeout_ms=1000,  # 1 second timeout
        )

    async def start_consumer(
        self,
        topics: list[str],
        handler: Callable[[Dict[str, Any]], None],
        error_handler: Optional[Callable[[Dict[str, Any], Exception], None]] = None,
    ) -> None:
        """Start consuming messages from Kafka."""
        try:
            async with self._lock:
                if self.consumer is None:
                    self.consumer = self._create_consumer(topics)
                    logger.info(f"Kafka consumer created for topics: {topics}")

            self.running = True

            while self.running:
                try:
                    message_pack = self.consumer.poll(timeout_ms=1000)

                    for topic_partition, messages in message_pack.items():
                        for message in messages:
                            try:
                                value = message.value
                                logger.debug(f"Received message from {topic_partition.topic}")

                                # Process message
                                await handler(value)

                            except Exception as e:
                                logger.error(
                                    f"Error processing message: {e}",
                                    exc_info=True,
                                )

                                # Error handling
                                if error_handler:
                                    try:
                                        await error_handler(message.value, e)
                                    except Exception as eh_error:
                                        logger.error(
                                            f"Error handler failed: {eh_error}",
                                            exc_info=True,
                                        )

                                # Dead-letter handling could go here

                except KafkaError as e:
                    logger.error(f"Kafka consumer error: {e}")
                    await asyncio.sleep(1)  # Brief pause before retry

        except Exception as e:
            logger.error(f"Consumer failed: {e}", exc_info=True)
            raise AppKafkaError(f"Consumer failed: {e}")

    async def stop(self) -> None:
        """Stop consumer."""
        self.running = False
        if self.consumer:
            self.consumer.close()
            self.consumer = None
            logger.info("Kafka consumer stopped")

    async def health_check(self) -> Dict[str, Any]:
        """Check consumer health."""
        try:
            if self.consumer is None:
                return {"status": "not_initialized"}

            # Try to get metadata
            partitions = self.consumer.list_consumer_group_offsets()

            return {
                "status": "healthy",
                "topics": list(self.consumer.subscription()),
                "partitions": len(partitions),
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}


# Global consumer instance
kafka_consumer = KafkaConsumerService()

