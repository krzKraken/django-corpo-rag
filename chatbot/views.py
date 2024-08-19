import os

import openai
from django.contrib import auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from dotenv import load_dotenv

from src import file_processing

from .models import Chat

# Create your views here.

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY)


# NOTE: Admin verify
def is_admin(user):
    return user.is_superuser


def welcome(request):
    return render(request, "welcome.html")


def ask_openai(message):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Eres un asistente, vas a responder a las preguntas que te hagan de una forma concreta y corta",
            },
            {
                "role": "user",
                "content": message,
            },
        ],
        max_tokens=150,
        temperature=1,
    )
    print(response)
    if response.choices[0].message.content:
        answer = response.choices[0].message.content.strip()
        return answer
    else:
        return "No answer received from chatgpt"


@login_required
def chatbot(request):
    chats = Chat.objects.filter(user=request.user)

    if request.method == "POST":
        message = request.POST.get("message")
        response = ask_openai(message)
        # NOTE: Create a chat for db
        chat = Chat(
            user=request.user,
            message=message,
            response=response,
            created_at=timezone.now,
        )
        chat.save()

        return JsonResponse(
            {"message": message, "response": response},
        )
    return render(request, "chatbot.html", {"chats": chats})


@login_required
def loadedfiles(request):
    documents = file_processing.files_in_docs()
    # Aquí harías la lógica para obtener los documentos

    # documents = [
    #     {"name": "nombre documento corto"},
    #     {"name": "nombre de documento otro mas largo"},
    #     {
    #         "name": "nombre de documento mucho mucho mas largo para pruebas, probando overflow en texto"
    #     },
    # ]
    return render(request, "loadedfiles.html", {"documents": documents})


def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect("chatbot")
        else:
            error_message = "Invalid username or password"
            return render(request, "login.html", {"error_message": error_message})
    else:
        return render(request, "login.html")


@user_passes_test(is_admin)
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]
        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect("chatbot")
            except:
                error_message = "Error creating account"
                return render(
                    request, "register.html", {"error_message": error_message}
                )
        else:
            error_message = "Password dont match"
            return render(request, "register.html", {"error_message": error_message})
    return render(request, "register.html")


def logout(request):
    auth.logout(request)
    return redirect("login")
