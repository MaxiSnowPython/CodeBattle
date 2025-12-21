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
from django.http import JsonResponse, HttpResponse


from .models import GameRoom, TaskSubmission
from .sandbox.sandbox import run_in_sandbox
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
    def post(self, request, id):
        room = get_object_or_404(GameRoom, id=id)
        result = None

        token = request.GET.get("token")
        try:
            access = AccessToken(token)
            user_id = access["user_id"]
        except TokenError:
            return HttpResponse("❌ JWT истёк")

        if "leave" in request.POST:
            if room.player1_id == user_id:
                room.player1 = None
            elif room.player2_id == user_id:
                room.player2 = None
            room.save()
            return redirect("/")

        if "submit_solution" in request.POST:
            code = request.POST.get("code", "").strip()
            if code:
                sandbox_result = run_in_sandbox(code, room.task)

                if "error" in sandbox_result:
                    result = {
                        "is_correct": False,
                        "error": sandbox_result["error"]
                    }
                else:
                    tests = json.loads(sandbox_result["output"])
                    passed_all = all(t["passed"] for t in tests)

                    if passed_all and not room.is_finished:
                        room.is_finished = True
                        room.winner_name = request.user.username
                        room.save()

                    TaskSubmission.objects.create(
                        user=request.user,
                        task=room.task,
                        code=code,
                        is_correct=passed_all
                    )

                    result = {
                        "is_correct": passed_all,
                        "tests": tests
                    }

        return render(
            request,
            "game/room.html",
            {
                "room": room,
                "result": result
            }
        )

