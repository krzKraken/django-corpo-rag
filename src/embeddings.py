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
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
        persist_directory=vectordb_path,
    )
    vectorstore.as_retriever()
