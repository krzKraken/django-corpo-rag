#!/usr/bin/env python3

import io
import os

import chromadb
import fitz
import pdfplumber
import PyPDF2
import pytesseract
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from PIL import Image
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


def create_embedding_from_text(text):
    vectordb_path = os.path.join(BASE_DIR, "vectordb")
    try:
        chromadb.PersistentClient(path=vectordb_path)
    except:
        print(colored(f"\n[!] Chromadb clients has already exist...\n", "yellow"))
    print(colored(f"\n[+] Creando embedding from text...\n"))
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_text(text)
    print(colored(f"Splits desde texto: {splits}", "blue"))
    vectorstore = Chroma.from_texts(
        texts=splits,
        embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
        persist_directory=vectordb_path,
    )
    vectorstore.as_retriever()


def create_embedding_from_pdf(name):

    full_path = os.path.join(MEDIA_ROOT, name)
    # Reading pdf file
    loader = PyPDFLoader(full_path)
    documents = loader.load()

    # Adding tables to documents
    with pdfplumber.open(full_path) as pdf:
        for page_index, page in enumerate(pdf.pages):
            tables_to_text = str(page.extract_tables())
            documents[page_index].page_content += tables_to_text

    # Adding text from images to documents
    pdf_document = fitz.open(full_path)

    # iterate peer page
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        images = page.get_images(full=True)

        if images:
            for img in images:
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]

                # convert to PIL image
                image = Image.open(io.BytesIO(image_bytes))

                # extract text from image using pytesseract
                extracted_text = pytesseract.image_to_string(image)

                # Adding text to page_content
                documents[
                    page_num
                ].page_content += f"\n[Texto extraído de la imagen en la página {page_num+1}]:\n{extracted_text}\n"

    pdf_document.close()
    with open("extracted_text.txt", "w") as f:
        f.write(str(documents))
    return
    print(colored(f"\ndocument:\n {documents[:]}", "yellow"))
    # return
    # TODO: obtener imagenes por pagina, luego hacer un append al doc.page_content

    print(colored(f"\n[+] File: {full_path} has been loaded successfully\n", "green"))
    print(colored(f"\n[+] pages: {len(documents)}, 'green'"))
    # Creating vectordb folder
    vectordb_path = os.path.join(BASE_DIR, "vectordb")
    try:
        chromadb.PersistentClient(path=vectordb_path)
    except:
        print(colored(f"[!] Chromadb client has already exist", "yellow"))

    # Creating embeddings and adding to vectordb
    print(colored(f"[+] Creando embedding from {full_path}", "blue"))
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)
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
