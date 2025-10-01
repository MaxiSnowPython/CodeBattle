from django.urls import path
from .views import *

urlpatterns = [
    path('hub/', JoinMatchView.as_view(), name='hub'),
]
