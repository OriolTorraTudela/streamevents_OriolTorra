from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("<int:event_pk>/send/", views.chat_send_message, name="send_message"),
    path("<int:event_pk>/messages/", views.chat_load_messages, name="load_messages"),
    path("message/<int:message_pk>/delete/", views.chat_delete_message, name="delete_message"),
    path("message/<int:message_pk>/highlight/", views.chat_highlight_message, name="highlight_message"),

]
