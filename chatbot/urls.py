from django.urls import path

from . import views

urlpatterns = [
    path("", views.welcome, name="welcome"),
    path("chatbot", views.chatbot, name="chatbot"),
    path("chatdocs", views.chatdocs, name="chatdocs"),
    path("login", views.login, name="login"),
    path("register", views.register, name="register"),
    path("logout", views.logout, name="logout"),
    path("loadedfiles", views.loadedfiles, name="loadedfiles"),
]
