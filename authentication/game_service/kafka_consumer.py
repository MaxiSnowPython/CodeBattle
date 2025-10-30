from kafka import KafkaConsumer, KafkaProducer
import json
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "game_service.settings")
django.setup()

from django.contrib.auth.models import User
from game_app.models import GameRoom, Task

consumer = KafkaConsumer(
    "games",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda v: json.loads(v.decode())
)

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode()
)

for message in consumer:
    event = message.value
    print("Получено событие:", event)
    players = event.get("players", [])

    if len(players) != 4:
        print("⚠️ Некорректный формат players:", players)
        continue

    player1, _ = User.objects.get_or_create(
        id=players[0],
        defaults={"username": players[1]}
    )
    player2, _ = User.objects.get_or_create(
        id=players[2],
        defaults={"username": players[3]}
    )

    task = Task.objects.first()
    if not task:
        print("❌ Нет задачи в базе, создайте хотя бы одну задачу")
        continue

    # Создаём комнату
    try:
        room = GameRoom.objects.create(
            player1=player1,
            player2=player2,
            task=task
        )
        print(f"✅ Комната создана с игроками {player1.username} vs {player2.username} и задачей {task.title}")

        # Отправляем событие в match_response
        response_event = {
            "event": "room_created",
            "room_id": room.id,
            "players": players
        }
        producer.send("match_response", response_event)
        producer.flush()

    except Exception as e:
        print(f"❌ Не удалось создать комнату: {e}")
