from kafka import KafkaConsumer
import json
import django
import os


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "game_service.settings")
django.setup()
from game_app.models import GameRoom 
consumer = KafkaConsumer(
    "games",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda v: json.loads(v.decode())
)

for message in consumer:
    event = message.value
    print("Получено событие:", message.value)
    players = event.get("players", [])  

    GameRoom.objects.create(
        room_id=event["room_id"],
        task_id=event["task_id"],
        player1_id = players[0],
        player1_name = players[1],
        player2_id = players[2],
        player2_name = players[3],
    )
    print(f"Комната {event['room_id']} создана в базе")