import os
import pika
import psycopg2
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MTGCardConsumer")

# RabbitMQ Configuration
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq.signalwave.svc.cluster.local')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', '5672'))
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'deploy')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'VMware123!')
QUEUE_NAME = os.getenv('RABBITMQ_CARD_QUEUE', 'mtgcards')

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

# Process card message
def process_card_message(ch, method, properties, body):
    try:
        message = json.loads(body)
        name = message['name']
        multiverse_id = message.get('multiverse_id')
        layout = message.get('layout')
        names = message.get('names')
        mana_cost = message.get('mana_cost')
        cmc = message.get('cmc')
        colors = message.get('colors')
        color_identity = message.get('color_identity')
        type_ = message.get('type')
        supertypes = message.get('supertypes')
        subtypes = message.get('subtypes')
        rarity = message.get('rarity')
        text = message.get('text')
        flavor = message.get('flavor')
        artist = message.get('artist')
        number = message.get('number')
        power = message.get('power')
        toughness = message.get('toughness')
        loyalty = message.get('loyalty')
        variations = message.get('variations')
        watermark = message.get('watermark')
        border = message.get('border')
        timeshifted = message.get('timeshifted')
        hand = message.get('hand')
        life = message.get('life')
        reserved = message.get('reserved')
        release_date = message.get('release_date')
        starter = message.get('starter')
        rulings = message.get('rulings')
        foreign_names = message.get('foreign_names')
        printings = message.get('printings')
        original_text = message.get('original_text')
        original_type = message.get('original_type')
        legalities = message.get('legalities')
        source = message.get('source')
        image_url = message.get('image_url')
        sets = message.get('sets')
        set_names = message.get('set_names')

        logger.info(f"Processing card: {name}")

        # Insert or update the card in PostgreSQL
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO mtg_cards (
                    name, multiverse_id, layout, names, mana_cost, cmc, colors, 
                    color_identity, type, supertypes, subtypes, rarity, text, 
                    flavor, artist, number, power, toughness, loyalty, variations, 
                    watermark, border, timeshifted, hand, life, reserved, release_date, 
                    starter, rulings, foreign_names, printings, original_text, 
                    original_type, legalities, source, image_url, sets, set_names
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (name)
                DO UPDATE SET
                    multiverse_id = EXCLUDED.multiverse_id,
                    layout = EXCLUDED.layout,
                    names = EXCLUDED.names,
                    mana_cost = EXCLUDED.mana_cost,
                    cmc = EXCLUDED.cmc,
                    colors = EXCLUDED.colors,
                    color_identity = EXCLUDED.color_identity,
                    type = EXCLUDED.type,
                    supertypes = EXCLUDED.supertypes,
                    subtypes = EXCLUDED.subtypes,
                    rarity = EXCLUDED.rarity,
                    text = EXCLUDED.text,
                    flavor = EXCLUDED.flavor,
                    artist = EXCLUDED.artist,
                    number = EXCLUDED.number,
                    power = EXCLUDED.power,
                    toughness = EXCLUDED.toughness,
                    loyalty = EXCLUDED.loyalty,
                    variations = EXCLUDED.variations,
                    watermark = EXCLUDED.watermark,
                    border = EXCLUDED.border,
                    timeshifted = EXCLUDED.timeshifted,
                    hand = EXCLUDED.hand,
                    life = EXCLUDED.life,
                    reserved = EXCLUDED.reserved,
                    release_date = EXCLUDED.release_date,
                    starter = EXCLUDED.starter,
                    rulings = EXCLUDED.rulings,
                    foreign_names = EXCLUDED.foreign_names,
                    printings = EXCLUDED.printings,
                    original_text = EXCLUDED.original_text,
                    original_type = EXCLUDED.original_type,
                    legalities = EXCLUDED.legalities,
                    source = EXCLUDED.source,
                    image_url = EXCLUDED.image_url,
                    sets = EXCLUDED.sets,
                    set_names = EXCLUDED.set_names
                """,
                (name, multiverse_id, layout, names, mana_cost, cmc, colors, 
                 color_identity, type_, supertypes, subtypes, rarity, text, 
                 flavor, artist, number, power, toughness, loyalty, variations, 
                 watermark, border, timeshifted, hand, life, reserved, release_date, 
                 starter, rulings, foreign_names, printings, original_text, 
                 original_type, legalities, source, image_url, sets, set_names)
            )
            conn.commit()
            logger.info(f"Card {name} processed successfully.")

    except Exception as e:
        logger.error(f"Error processing card message: {e}")

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
        on_message_callback=process_card_message,
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
