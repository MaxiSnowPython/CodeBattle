from django.urls import path
from .views import *

urlpatterns = [

    path('room/<str:id>/', RoomView.as_view(),name="room"),


]






