import os

import openai
from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from dotenv import load_dotenv

from src import file_processing

from .models import Chat

# Ruta almacenamiento de documentos
DOCS_DIR = os.path.join(settings.MEDIA_ROOT)

# Views
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
                "content": "Eres un asistente virtual, vas a responder a las preguntas que te hagan de una forma corta, concreta y precisa, te llamas Corporito.",
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
            {
                "message": message,
                "response": response,
            },
        )
    return render(request, "chatbot.html", {"chats": chats})


def ask_embedding(message):
    # TODO: Embedding answer here...
    return f"programar respuesta para {message}"


@login_required
def chatdocs(request):
    if request.method == "POST":
        message = request.POST.get("message")
        response = ask_embedding("pregunta del usuario")
        chat = Chat(
            user=request.user,
            message=message,
            response=response,
            created_at=timezone.now,
        )
        chat.save()
        return JsonResponse(
            {
                "message": message,
                "response": response,
            }
        )

    return render(request, "chatdocs.html")


@login_required
def loadedfiles(request):

    documents = file_processing.files_in_docs()
    # Asegurarnos que docs existe
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR)

    # Manejo de carga de archivos
    if request.method == "POST" and request.FILES.get("documento_pdf"):
        archivo_pdf = request.FILES["documento_pdf"]
        # Validar que el archivo sea un pdf
        if archivo_pdf.content_type != "application/pdf":
            return render(
                request,
                "loadedfiles.html",
                {
                    "documents": documents,
                    "error_message": "Solo se permiten archivos pdf por el momento",
                },
            )
        # Almacenamiento seguro del archivo
        fs = FileSystemStorage(location=DOCS_DIR)
        archivo_nombre = fs.save(archivo_pdf.name, archivo_pdf)
        messages.success(
            request, f"El archivo '{archivo_nombre}' se ha cargado correctamente"
        )
        return redirect("loadedfiles")

    return render(
        request,
        "loadedfiles.html",
        {
            "documents": documents,
        },
    )


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
