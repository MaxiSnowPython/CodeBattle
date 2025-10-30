from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.db import models
from .models import *
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken, TokenError
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.views import View
from django.contrib.auth.hashers import make_password
from kafka import KafkaProducer
import json
from game_app.serializers import GameRoomSerializer
from rest_framework.response import Response
from rest_framework import status

# Create your views here.

class RoomView(View):
    def get(self,request,id,*args, **kwargs):
        token = request.GET.get("token")
        try:
            access = AccessToken(token)  # проверка токена
            user_id = access["user_id"]
            user = User.objects.get(id=user_id)
        except TokenError:
            return HttpResponse("❌ Токен недействителен или истёк. <a href='/auth/login/'>Войти заново</a>")

        try:
            room = GameRoom.objects.get(id=id)
        except GameRoom.DoesNotExist:
            return HttpResponse("Комната не найдена")
    

        return render(request, "game/room.html", {
                "room":room,
                "user": user,
        })
    def post(self,request,id):
        token = request.GET.get("token")
        try:
            access = AccessToken(token)
            user_id = access["user_id"]
            user = User.objects.get(id=user_id)
        except TokenError:
            return HttpResponse("❌ Токен недействителен или истёк. <a href='/auth/login/'>Войти заново</a>")
        try:
            room = GameRoom.objects.get(id=id)
        except GameRoom.DoesNotExist:
            return HttpResponse("Комната не найдена")
    
        if "leave" in request.POST:
            GameRoom.objects.filter(user=user).delete()
            status = "leave"
            return HttpResponse("Комната не найдена")
        return render(request, "game/room.html", {
                "room":room,
                "user": user,
        })