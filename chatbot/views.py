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
from termcolor import colored

from src import file_processing
from src.embeddingchat import get_embedding_response
from src.embeddings import create_embedding_from_pdf, get_unique_sources_list
from src.response_to_html import format_to_html

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
                "content": "Eres un asistente virtual de una empresa de equipos medicos, vas a responder como su asistente personal."
                "",
            },
            {
                "role": "user",
                "content": message,
            },
        ],
        max_tokens=500,
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
        response = format_to_html(response)
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
    response = get_embedding_response(message)

    return response


@login_required
def blog(request):
    if request.method == "POST":
        message = request.POST.get("message")
        # TODO: Implementar guardado en base de datos y creacion de embeddings
    return render(request, "blog.html")


@login_required
def chatdocs(request):
    if request.method == "POST":
        message = request.POST.get("message")
        response = ask_embedding(message)
        response = format_to_html(response)
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
    try:

        documents = get_unique_sources_list()
    except:
        return render(request, "loadedfiles.html")
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
        if archivo_pdf.name in documents:
            print(colored("\n[!] Existe", "red"))
            error_message = "El archivo o nombre del pdf ya existe en la base de datos"
            return render(
                request,
                "loadedfiles.html",
                {"documents": documents, "error_message": error_message},
            )
        else:
            print(colored(f"[!] No existe", "red"))
            print(
                colored(
                    f"\n[+] El archivo {archivo_pdf} no existia en la base de datos, creandolo....",
                    "blue",
                )
            )
            fs = FileSystemStorage(location=DOCS_DIR)
            archivo_nombre = fs.save(archivo_pdf.name, archivo_pdf)

            create_embedding_from_pdf(archivo_pdf.name)

            print(colored(f"\n[!] Archivo_pdf: {archivo_pdf}", "red"))
            print(colored(f"\n[!] Documents: {documents}", "red"))
            messages.success(
                request, f"El archivo '{archivo_pdf}' se ha cargado correctamente"
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
            return redirect("welcome")
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
