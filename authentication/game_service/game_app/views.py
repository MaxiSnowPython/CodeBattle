from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.db import models
from .models import *

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.views import View
from django.contrib.auth.hashers import make_password
from kafka import KafkaProducer
import json

# Create your views here.

class RoomView(View):
    def get(self,request,room_id):
        token = request.GET.get("token")
        if not token:
             return HttpResponse('<a href="/auth/login/">Войти</a>')
        try:
            room = GameRoom.objects.get(room_id=room_id)
        except GameRoom.DoesNotExist:
            return HttpResponse("Комната не найдена")

        return render(request, "game/room.html", {
                "room":room.room_id,
                "player1_id":room.player1_id,
                "player1_username":room.player1_name,
                "player2_id":room.player2_id,
                "player2_username":room.player2_name,
        })
    #lox