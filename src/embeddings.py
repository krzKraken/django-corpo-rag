#!/usr/bin/env python3

import os

import chromadb
import PyPDF2
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from termcolor import colored

from corpo_chatbot import settings

load_dotenv()
# openai api key

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MEDIA_ROOT = settings.MEDIA_ROOT
BASE_DIR = settings.BASE_DIR


def read_pdf(pdf_name):
    # Read pdf from docs
    full_path = os.path.join(BASE_DIR, f"/docs/{pdf_name}")
    with open(full_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in range(len(reader.pages)):
            text += reader.pages[page].extract_text()
    return text


def create_embedding_from_pdf(name):

    full_path = os.path.join(MEDIA_ROOT, name)
    # Reading pdf file
    loader = PyPDFLoader(full_path)
    # TODO: obtener imagenes por pagina, luego hacer un append al doc.page_content
    # documents = loader.load()
    # for doc in documents:
    #   contenido = doc.page_content
    #   contenido_modificado = contenido + "\n informacion adicional: "
    #   doc.page_content = contenido_modificado

    doc = loader.load()
    print(colored(f"\n[+] File: {full_path} has been loaded successfully\n", "green"))
    print(colored(f"\n[+] pages: {len(doc)}, 'green'"))
    # Creating vectordb folder
    vectordb_path = os.path.join(BASE_DIR, "vectordb")
    try:
        chromadb.PersistentClient(path=vectordb_path)
    except:
        print(colored(f"[!] Chromadb client has already exist", "yellow"))

    # Creating embeddings and adding to vectordb
    print(colored(f"[+] Creando embedding from {full_path}", "blue"))
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(doc)
    print(splits)
    """ for doc in splits:
        page_number = doc.metadata.get("page")
        page_content = doc.page_content
        print(f"pagina: {page_number}")
        print(f"contenido: {page_content}")
        print("-" * 50)
    return """
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
        persist_directory=vectordb_path,
    )
    vectorstore.as_retriever()


def get_unique_sources_list():
    vectordb_path = os.path.join(BASE_DIR, "vectordb")
    persistent_client = chromadb.PersistentClient(path=vectordb_path)
    collection_data = persistent_client.get_collection("langchain").get(
        include=["embeddings", "documents", "metadatas"]
    )

    # Extrae los metadatos
    metadatas = collection_data["metadatas"]

    # Obtén los valores únicos de 'source'
    sources = set()
    if metadatas:
        for metadata in metadatas:
            source = metadata.get("source", None)
            if source:
                sources.add(source)
    else:
        print(colored(f"[!] No metadatas loaded", "red"))

    # Obtener solo el nombre de archivo de cada ruta
    file_names = list(set(source.split("/")[-1] for source in sources))

    return file_names
