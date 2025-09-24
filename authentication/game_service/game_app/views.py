from django.shortcuts import render
from kafka import KafkaConsumer
import json
# Create your views here.


# создаём консюмер для топика "games"
consumer = KafkaConsumer(
    "games",  # топик, из которого читаем
    bootstrap_servers="localhost:9092",  # адрес Kafka
    value_deserializer=lambda v: json.loads(v.decode())  # декодируем JSON обратно в словарь
)

# читаем сообщения
for message in consumer:
    event = message.value  # вот здесь уже словарь Python
    print("Получено событие:", event)
    
    # можно обработать событие, например создать игру
    room_id = event["room_id"]
    players = event["players"]
    task_id = event["task_id"]
    
    # тут код для запуска игры для этих игроков
