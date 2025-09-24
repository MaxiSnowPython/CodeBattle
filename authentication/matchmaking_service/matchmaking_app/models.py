from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class MatchQueue(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']

class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    expected_output = models.CharField(max_length=500)  # Ожидаемый результат
    initial_code = models.TextField(blank=True, null=True)  # Начальный код для пользователя
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class GameRoom(models.Model):
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_as_player1', null=True,blank=True)
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_as_player2',null=True,blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE,null=True,blank=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_finished = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Room {self.id}: {self.player1.username} vs {self.player2.username}"

class TaskSubmission(models.Model):
    room = models.ForeignKey(GameRoom, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.TextField()
    result = models.TextField(blank=True, null=True)
    is_correct = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['submitted_at']