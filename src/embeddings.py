#!/usr/bin/env python3

import os

import chromadb
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


def create_embedding_from_pdf(name):

    full_path = os.path.join(MEDIA_ROOT, name)
    loader = PyPDFLoader(full_path)
    doc = loader.load()
    print(colored(f"\n[+] File: {full_path} has been loaded successfully\n", "green"))
    print(colored(f"\n[+] pages: {len(doc)}, 'green'"))
    try:
        vectordb_path = os.path.join(BASE_DIR, "vectordb")
        chromadb.PersistentClient(path=vectordb_path)

    except:
        print(colored(f"[!] Chromadb client has already exist", "orange"))
