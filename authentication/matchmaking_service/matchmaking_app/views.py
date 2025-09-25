from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.db import models
from .models import MatchQueue, GameRoom, Task, TaskSubmission
from .utils import execute_python_code, check_answer
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.views import View
from django.contrib.auth.hashers import make_password
from kafka import KafkaProducer
import json

User = get_user_model()
class JoinMatchView(View):


    def get(self, request):
        token = request.GET.get("token")
        # Получаем токен
        if not token:
            return HttpResponse('<a href="http://127.0.0.1:8000/auth/login/">Войти</a>')
        # Если нет токена то перекидует на логин
        try:
            access = AccessToken(token)
           
            user_id = access["user_id"]
            username = access.get("username", f"user_{user_id}")
            # Получаем инфу с токена
            
            # Попробуй найти пользователя, если нет - создай
            try:
                user = User.objects.get(id=user_id)
                if user.username != username:
                    user.username = username
                    user.save()
            except User.DoesNotExist:
                user = User(id=user_id, username=username)
                user.set_password("gey123e")
                user.save()
            
            # Проверяем, не в активной игре ли пользователь
            active_room = GameRoom.objects.filter(
                models.Q(player1=user) | models.Q(player2=user),
                is_active=True,
                is_finished=False
            ).first()
            
            if active_room:
                return redirect(f'/match/room/{active_room.id}/?token={token}')
           
            # Проверяем статус очереди
            status = None
            error = None
            if "leave" in request.GET:
                MatchQueue.objects.filter(user=user).delete()
                status = "leave"
                
            
            if MatchQueue.objects.filter(user=user).exists():
                status = 'waiting'
            
            return render(request, "matchmaking_app/hub.html", {
                "user": user, 
                "status": status,
                "error": error
            })
            
        except Exception as e:
            print(f"JoinMatchView error: {str(e)}")
            return HttpResponse(f'Ошибка: {str(e)} <a href="http://127.0.0.1:8000/auth/login/">Войти заново</a>')
        

    queue = []
    # создаём Kafka продюсер
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
        # Проверяем очередь
        waiting_player = MatchQueue.objects.exclude(user=user).first()
        

        if waiting_player:
            # Создаём комнату
            room = GameRoom.objects.create(player1=waiting_player.user, player2=user)
            MatchQueue.objects.filter(user=user).delete()
            waiting_player.delete()

            # --- добавляем событие в Kafka ---
            event = {
                "event": "game_created",
                "room_id": room.id,
                "players": [waiting_player.user.username,username],
                "task_id": 5  # например, id задачи для игры
            }
            self.producer.send("games", event)
            # -----------------------------------
            
            return redirect(f"/match/room/{room.id}/?token={token}")
        else:
            # Добавляем себя в очередь, если никого нет
            MatchQueue.objects.get_or_create(user=user)
            return redirect(f"/match/hub/?token={token}")

class RoomView(View):
    def get(self,request,room_id):
        token = request.GET.get("token")
        if not token:
            return HttpResponse('<a href="http://127.0.0.1:8000/auth/login/">Войти</a>')
        access = AccessToken(token)
        user_id = access["user_id"]
        user = User.objects.get(id=user_id)
        try:
            room = GameRoom.objects.get(id=room_id, is_active=True)
        except GameRoom.DoesNotExist:
            return redirect(f"/match/hub/?token={token}")
        
        opponent = room.player2 if user == room.player1 else room.player1
            


        return render(request,"matchmaking_app/room.html",{
            "room": room,
            "user": user,
            "opponent": opponent,
        })
    def post(self,request,room_id):
        token = request.GET.get("token")
        if not token:
            return HttpResponse('<a href="http://127.0.0.1:8000/auth/login/">Войти</a>')

        access = AccessToken(token)
        user_id = access["user_id"]
        user = User.objects.get(id=user_id)
        room = GameRoom.objects.get(id=room_id,is_active = True)
        opponent = room.player2 if user == room.player1 else room.player1

        if "leaveroom" in request.POST:
            if user == room.player1:
                room.player1 = None
            elif user == room.player2:
                room.player2 = None
            room.save()
        
        if not room.player1 or not room.player2:
            room.delete()
            return redirect(f"/match/hub/?token={token}")

    # если у игрока нет оппонента → сразу на хаб
        if not opponent:
            return redirect(f"/match/hub/?token={token}")
        