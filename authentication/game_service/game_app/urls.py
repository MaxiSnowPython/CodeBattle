from django.urls import path
from .views import *
urlpatterns = [
   path("room/<int:id>/", RoomView.as_view(), name="room"),
]




