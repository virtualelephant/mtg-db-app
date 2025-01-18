import os
import time
import pika
import logging
from mtgsdk import Card
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MTGCardPublisher")

# RabbitMQ Configuration
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq.signalwave.svc.cluster.local') 
rabbitmq_port_env = os.getenv('RABBITMQ_PORT', '5672')
if rabbitmq_port_env.startswith('tcp://'):
    RABBITMQ_PORT = int(rabbitmq_port_env.split(":")[-1])
else:
    RABBITMQ_PORT = int(rabbitmq_port_env)
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'deploy')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'VMware123!')
QUEUE_NAME = os.getenv('RABBITMQ_QUEUE', 'mtgcards') 
MESSAGE_RATE = float(os.getenv('MESSAGE_RATE', 1.0))

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)

def create_connection():
    retry_delay = 5
    max_delay  = 60  # Cap the delay
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials))
            logger.info("Successfully connected to RabbitMQ")
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            logger.error({"error": str(e), "message": f"Retrying connection in {retry_delay} seconds..."})
            time.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, max_delay)

# Establish connection to RabbitMQ
#connection = create_connection()
#channel = connection.channel()
#channel.queue_declare(queue=QUEUE_NAME, durable=True, arguments={"x-queue-type": "quorum"})
#logger.info("Successfully declared queue")

def publish_card(card):
    """Publish a card's data to the RabbitMQ queue."""
    try:
        card_message = {
            "name": card.name,
            "mana_cost": card.mana_cost,
            "type": card.type,
            "rarity": card.rarity,
            "set": card.set,
            "text": card.text,
            "power": card.power,
            "toughness": card.toughness
        }
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=str(card_message),
            properties=pika.BasicProperties(
                delivery_mode=2  # Make message persistent
            )
        )
        logger.info(f"Published card: {card.name}")
    except Exception as e:
        logger.error(f"Failed to publish card {card.name}: {e}")

def fetch_cards(queue):
    """Fetch cards and add them to the queue"""
    try:
        from datetime import datetime
        start_time = datetime.now()

        logger.info(f"{start_time}: Fetching all MTG cards...")
        for card in Card.all():
            queue.put(card) # Add cards to the queue
            logger.debug(".", end="", flush=True) # DEBUG LOG
        end_time = datetime.now()
        logger.info(f"{end_time}: Successfully fetched all cards")
        logger.info(f"Total time to fetch cards: {end_time - start_time}")
    except Exception as e:
        logger.error(f"Error fetching cards: {e}")

def publish_cards_from_queue(queue, connection):
    """Consume cards from the queue and publish to RabbitMQ"""
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True, arguments={"x-queue-type": "quorum"})
    while not queue.empty():
        card = queue.get()
        publish_card(channel, card)
        queue.task_done()
        time.sleep(1.0 / MESSAGE_RATE)

if __name__ == "__main__":
    card_queue = Queue(maxsize=100)  # Queue for holding cards
    connection = create_connection()

    # Use a ThreadPoolExecutor for parallel fetching and publishing
    with ThreadPoolExecutor(max_workers=2) as executor:
        fetch_future = executor.submit(fetch_cards, card_queue)
        publish_future = executor.submit(publish_cards_from_queue, card_queue, connection)

        # Wait for both tasks to complete
        for future in as_completed([fetch_future, publish_future]):
            try:
                future.result()
            except Exception as e:
                logger.error(f"Error in execution: {e}")

    # Close connection
    connection.close()
    logger.info("RabbitMQ connection closed.")
