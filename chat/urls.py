from django.urls import path

from . import views

urlpatterns = [
    path("", views.room_global, name="chat_global"),
    path("c/<slug:slug>/", views.room_contest, name="chat_contest"),
    path("api/<str:room>/messages/", views.api_messages, name="chat_api_messages"),
    path("api/<str:room>/send/", views.api_send, name="chat_api_send"),
]
