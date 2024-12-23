import json
import os
from kafka import KafkaProducer
from dotenv import load_dotenv

load_dotenv(verbose=True)

def produce(data,key, topic):
    producer = KafkaProducer(
        bootstrap_servers=os.environ['BOOTSTRAP_SERVERS'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    producer.send(
        topic,
        value=data,
        key=key.encode('utf-8')
    )
    producer.flush()