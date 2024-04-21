from django.urls import path
from .views import ChatBot

urlpatterns = [
    path('', ChatBot().main, name='chatbot')
]