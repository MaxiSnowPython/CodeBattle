from django.urls import path
from .views import *

urlpatterns = [
    path('hub/', JoinMatchView.as_view(), name='hub'),
    path('room/<int:room_id>/',RoomView.as_view(),name="room"),
]
