import os
import pika
import psycopg2
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MTGSetConsumer")

# RabbitMQ Configuration
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq.services.svc.cluster.local')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', '5672'))
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'deploy')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'VMware123!')
QUEUE_NAME = os.getenv('RABBITMQ_SET_QUEUE', 'mtgsets')

# Postgres Configuration
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'postgres.mtg.svc.cluster.local')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'mtg_database')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'deploy')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'VMware123!')

# Connect to PostgreSQL
def connect_postgres():
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD
        )
        logger.info("Connected to PostgreSQL successfully.")
        return conn
    except Exception as e:
        logger.error(f"Error connecting to PostgreSQL: {e}")
        raise

# Process set message
def process_set_message(ch, method, properties, body):
    try:
        message = json.loads(body)
        set_code = message['set_code']
        name = message['name']
        release_date = message.get('release_date')
        total_cards = message.get('total_cards', 0)

        logger.info(f"Processing set: {name} ({set_code})")

        # Insert or update the set in PostgreSQL
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO mtg_sets (set_code, name, release_date, total_cards)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (set_code)
                DO UPDATE SET
                    name = EXCLUDED.name,
                    release_date = EXCLUDED.release_date,
                    total_cards = EXCLUDED.total_cards
                """,
                (set_code, name, release_date, total_cards)
            )
            conn.commit()
            logger.info(f"Set {name} ({set_code}) processed successfully.")

    except Exception as e:
        logger.error(f"Error processing set message: {e}")

# Connect to RabbitMQ
def connect_rabbitmq():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials
    )
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True, arguments={"x-queue-type": "quorum"})
    logger.info("Connected to RabbitMQ and queue declared successfully.")
    return connection, channel

if __name__ == "__main__":
    # Establish connections
    conn = connect_postgres()
    rabbitmq_connection, rabbitmq_channel = connect_rabbitmq()

    # Consume messages
    rabbitmq_channel.basic_consume(
        queue=QUEUE_NAME,
        on_message_callback=process_set_message,
        auto_ack=True
    )

    logger.info("Waiting for messages...")
    try:
        rabbitmq_channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("Stopping consumer...")
    finally:
        rabbitmq_channel.close()
        rabbitmq_connection.close()
        conn.close()
        logger.info("Connections closed.")
