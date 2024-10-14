# chat/urls.py

from django.urls import path
from .views import room

urlpatterns = [
    path('chat/', room, name='room'),
]
