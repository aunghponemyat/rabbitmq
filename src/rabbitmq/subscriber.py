import copy
import json

import pika
from pika.credentials import PlainCredentials
from sqlalchemy.orm import sessionmaker
from structlog import get_logger

from rabbitmq.database.db_models import PayloadMsg, init_db
from rabbitmq.eventlog import EventLogger
from rabbitmq.models.config import Settings, get_settings

logger: EventLogger = get_logger()
settings: Settings = get_settings()
Session = sessionmaker(bind=init_db(settings.db_dsn))

valid_events = {'entry', 'checkout', 'exterminate', 'validate'}


def event_translator(event: str):
    event_mapping = {
        'entry': 'ENTERED',
        'checkout': 'CHECKED_OUT',
        'exterminate': 'EXTERMINATED',
        'validate': 'VALIDATED'
    }
    return event_mapping.get(event, 'UNKNOWN')

def setup_rabbitmq_consumer():
    credentials = PlainCredentials(
        username=settings.rbq_username,
        password=settings.rbq_password
    )
    connection_parameters = pika.ConnectionParameters(
        host=settings.rbq_host,
        port=settings.rbq_port,
        credentials=credentials,
        virtual_host=settings.rbq_vhost
    )
    # Create a new connection
    connection = pika.BlockingConnection(connection_parameters)
    # Open a channel
    channel = connection.channel()
    return connection, channel

def start_consumer():
    try:
        _, channel = setup_rabbitmq_consumer()
        channel.queue_declare(settings.rbq_queue_name, durable=True)
        # Callback function to process received messages
        def callback(_, __, ___, body: bytes):
            
            decoded_body = body.decode('utf-8')
            serialized_data = json.loads(decoded_body)
            event = serialized_data.get("event_type")
            if event in valid_events:
                logger.info("Received", message="accepted", data=serialized_data)
                execute_message(serialized_data)
            else:
                logger.info("Received", message=f"rejected: invalid event {event}", data=serialized_data)
        channel.basic_consume(queue=settings.rbq_queue_name,
                            on_message_callback=callback,
                            auto_ack=True)
        print('[*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()

    except KeyboardInterrupt:
        pass

def execute_message(data: dict):
    try:
        copy_object = copy.deepcopy(data)
        copy_object.pop('timestamp', None)
        event_type = copy_object.get("event_type")
        cid = copy_object.get("client_id")
        translated_event = event_translator(event_type)
        copy_object["event_type"] = translated_event
        operate_db(copy_object)
        logger.info(translated_event, client_id=cid, status='Done')
    except Exception as e:
        print(f"Processing Error: {e}")

def operate_db(data):
    with Session() as session:
        payload = PayloadMsg(**data)
        session.add(payload)
        session.commit()

if __name__ == '__main__':
    start_consumer()

