from kafka import KafkaConsumer
import json
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "matchmaking_service.settings")
django.setup()

from matchmaking_app.models import MatchQueue

consumer = KafkaConsumer(
    "match_response",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda v: json.loads(v.decode())
)

for message in consumer:
    event = message.value
    if event["event"] == "room_created":
        room_id = event["room_id"]
        players = event["players"]
        print(f"✅ Матчмейкинг получил room_id={room_id} для игроков {players}")
        
        # Тут можно обновить свой internal state или notify frontend
        for player_id in [players[0], players[2]]:  # первые и третьи элементы — ID игроков
            mq = MatchQueue.objects.filter(user_id=player_id).first()
            if mq:
                mq.room_id = room_id
                mq.save()
                print(f"   🔹 Обновлен room_id для пользователя {player_id}")