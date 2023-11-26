from django.urls import path
from . import gpt_bot

urlpatterns = [
    path('', gpt_bot.chatbot, name='chatbot'),
]