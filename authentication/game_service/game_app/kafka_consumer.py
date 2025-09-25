from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    "games",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda v: json.loads(v.decode())
)

for message in consumer:
    print("Получено событие:", message.value)