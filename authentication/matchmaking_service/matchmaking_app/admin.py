from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(GameRoom)
admin.site.register(MatchQueue)
admin.site.register(TaskSubmission)
admin.site.register(Task)
