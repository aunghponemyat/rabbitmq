# RabbitMQ test

## Introduction
This project focuses on the implementation of RabbitMQ message broker with simple application setup using poetry as a package manager. Pika libray is used for rabbimq integration with python.

## Prerequisites
- Python 3.10+
- Poetry version 1.7.1+
- TiDB or Mysql equivalent

## Installation & Setup
```
foo~$ ./scripts/setup
```


## Run tips
Just run the <b>subscriber.py</b> file to start consuming messages
```
foo~$ poetry shell (or) source .venv/bin/activate
foo~$ python src/rabbitmq/subscriber.py
```
For sending messages, run
```
foo~$ poetry shell (or) source .venv/bin/activate
foo~$ python src/rabbitmq/publisher.py
```