import json  # Import the json module for serialization
from rabbitmq.models.config import Settings, get_settings
import pika
from pika.credentials import PlainCredentials

settings: Settings = get_settings()

credentials = PlainCredentials(
    username=settings.rbq_username,
    password=settings.rbq_password
)

# Set up connection parameters
connection_parameters = pika.ConnectionParameters(
    host=settings.rbq_host,
    port=settings.rbq_port,
    virtual_host=settings.rbq_vhost,
    credentials=credentials
)

# Connect to RabbitMQ server on localhost
connection = pika.BlockingConnection(connection_parameters)
channel = connection.channel()

channel.queue_declare(queue=settings.rbq_queue_name, durable=True)

# Define a dictionary to send as the message body
message_dict = {
    "event_type": "entry",
    "client_id": "61320008",
    "message_body": "This is a sample message",
    "remark": "Just for test",
    "timestamp": 12789901
}

# Serialize the dictionary to a JSON string
message_body = json.dumps(message_dict)

# Publish the JSON string to the 'test' queue
channel.basic_publish(exchange='',
                      routing_key=settings.rbq_queue_name,
                      body=message_body)

print(f" [x] Sent {message_body}")

# Close the connection
connection.close()
