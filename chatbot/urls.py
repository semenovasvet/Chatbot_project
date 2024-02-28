from django.urls import path
from .botFunctions import ChatBot

urlpatterns = [
    path('', ChatBot().main, name='chatbot')
]