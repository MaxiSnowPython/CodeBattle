from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.views import View
from django.contrib import messages
from django.contrib.auth import login
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
import requests

from django.http import JsonResponse
MATCH_SERVICE_URL = "http://localhost:8002/match/create_user/"  # endpoint в match_service


class RegisterView(FormView):
    template_name = 'auth/register_form.html'
    form_class = UserCreationForm
    def form_valid(self, form):
        # Сохраняем пользователя
        user = form.save()
        # Логиним пользователя
        login(self.request, user)
        
        # Создаем токен
        refresh = RefreshToken.for_user(user)
        refresh['username']= user.username
        access_token = str(refresh.access_token)
        
        # Редирект на матчмейкинг
        return redirect(f"http://127.0.0.1:8001/match/hub/?token={access_token}")
    
    def form_invalid(self, form):
        username = self.request.POST.get("username")
        if User.objects.filter(username=username).exists():
            messages.error(self.request,"Такого пользователя есть")

        return super().form_invalid(form)
        
    




class CustomLoginView(LoginView):
    template_name = 'auth/login_form.html'
 

    def form_valid(self, form):
        # Логиним пользователя вручную (без редиректа)
        user = form.get_user()
        
        login(self.request, user)
        
        # Создаем токен
        refresh = RefreshToken.for_user(user)
        refresh['username']= user.username
        print(refresh['username'])
        access_token = str(refresh.access_token)
        # Редирект на матчмейкинг
        return redirect(f"http://127.0.0.1:8001/match/hub/?token={access_token}")
    
    def form_invalid(self, form):
        username = self.request.POST.get("username")
        if not User.objects.filter(username=username).exists():
            messages.error(self.request,"Такого пользователя нету")
        return super().form_invalid(form)
    