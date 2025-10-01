from django.db import models
from django.contrib.auth import get_user_model

# Create your models here

User = get_user_model()

class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    expected_output = models.CharField(max_length=500)  # Ожидаемый результат
    initial_code = models.TextField(blank=True, null=True)  # Начальный код для пользователя
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class GameRoom(models.Model):
    room_id = models.CharField(max_length=50, unique=True)  


    player1_id = models.IntegerField()  
    player1_name = models.CharField(max_length=100)

    player2_id = models.IntegerField()
    player2_name = models.CharField(max_length=100)

    task_id = models.IntegerField()     

    is_active = models.BooleanField(default=True)
    is_finished = models.BooleanField(default=False)

    winner_id = models.IntegerField(null=True, blank=True)
    winner_name = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)