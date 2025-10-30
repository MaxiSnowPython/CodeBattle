from rest_framework import serializers
from .models import GameRoom

class GameRoomSerializer(serializers.ModelSerializer):
    # Дополнительно добавляем username для удобства
    player1_username = serializers.CharField(source='player1.username', read_only=True)
    player2_username = serializers.CharField(source='player2.username', read_only=True)

    class Meta:
        model = GameRoom
        fields = [
            'id', 
            'player1', 
            'player1_username',
            'player2', 
            'player2_username', 
            'task', 
            'is_active', 
            'is_finished', 
            'winner_name'
        ]