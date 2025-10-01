from django.urls import path
from .views import *

urlpatterns = [

    path('room/<str:room_id>/', RoomView.as_view(),name="room"),

]






