from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class MatchQueue(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    room_id = models.IntegerField(null=True, blank=True)
    class Meta:
        ordering = ['created_at']
