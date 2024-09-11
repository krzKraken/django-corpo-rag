#!/usr/bin/env python

# TODO: implementar
import os

import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from PyPDF2 import PdfReader

from corpo_chatbot import settings

BASE_DIR = settings.BASE_DIR
# Si usas Windows, especifica la ruta de Tesseract
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def read_pdf(pdf_name):
    """
    Lee el texto y las imágenes de un PDF, y convierte las imágenes en texto usando OCR.
    """
    # Ruta completa al archivo PDF
    full_path = os.path.join(BASE_DIR, f"docs/{pdf_name}")

    # Leer texto del PDF
    text = ""
    try:
        with open(full_path, "rb") as pdf_file:
            reader = PdfReader(pdf_file)
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text() or ""
    except Exception as e:
        print(f"Error al leer el texto del PDF: {e}")

    # Extraer imágenes del PDF y convertirlas a texto
    try:
        images = convert_from_path(full_path)
        for image in images:
            # Aplicar OCR a cada imagen
            text += pytesseract.image_to_string(image)
    except Exception as e:
        print(f"Error al procesar las imágenes del PDF: {e}")

    return text


# Ejemplo de uso
# pdf_name = "documento.pdf"  # Cambia por el nombre de tu PDF
# contenido_pdf = read_pdf(pdf_name)
# print(contenido_pdf)
