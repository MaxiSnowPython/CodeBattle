from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.db import models
from .models import MatchQueue
from django.shortcuts import get_object_or_404
from django.views import View
from kafka import KafkaProducer
import json 
import requests

User = get_user_model()
class JoinMatchView(View):
    def get(self, request):
        token = request.GET.get("token")

        if not token:
            return HttpResponse('<a href="http://127.0.0.1:8000/auth/login/">Войти</a>')

        try:
            access = AccessToken(token)
           
            user_id = access["user_id"]
            username = access.get("username", f"user_{user_id}")

            try:
                user = User.objects.get(id=user_id)
                if user.username != username:
                    user.username = username
                    user.save()
            except User.DoesNotExist:
                user = User(id=user_id, username=username)
                user.set_password("gey123e")
                user.save()
            

            status = None
            error = None
            if "leave" in request.GET:
                MatchQueue.objects.filter(user=user).delete()
                status = "leave"
                
            
            if MatchQueue.objects.filter(user=user).exists():
                status = 'waiting'
            mq = MatchQueue.objects.filter(user=user).first()
            if mq and mq.room_id:
                room_id = mq.room_id
                mq.delete()
                return redirect(f"http://localhost:8002/game/room/{room_id}/?token={token}")
            return render(request, "matchmaking_app/hub.html", {
                "user": user, 
                "status": status,
                "error": error
            })
            
        except Exception as e:
            print(f"JoinMatchView error: {str(e)}")
            return HttpResponse(f'Ошибка: {str(e)} <a href="http://127.0.0.1:8000/auth/login/">Войти заново</a>')
        

    queue = []

    producer = KafkaProducer(
            bootstrap_servers="localhost:9092",
            value_serializer=lambda v: json.dumps(v).encode()
    )
    def post(self, request):
        token = request.GET.get("token")
        if not token:
            return HttpResponse('<a href="/auth/login/">Войти</a>')

        access = AccessToken(token)
        user_id = access["user_id"]
        user = User.objects.get(id=user_id)
        username = access.get("username", f"user_{user_id}")

        waiting_player = MatchQueue.objects.exclude(user=user).first()

        if waiting_player:

            event = {
                "event": "match_found",
                "players": [
                    waiting_player.user.id,
                    waiting_player.user.username,
                    user.id,
                    username
                ],
            }
            self.producer.send("games", event)
            MatchQueue.objects.get_or_create(user=user)
            return redirect(f"/match/hub/?token={token}")
        else:
            MatchQueue.objects.get_or_create(user=user)
            return redirect(f"/match/hub/?token={token}")
