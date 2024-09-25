import os

import pdfplumber

from corpo_chatbot import settings

BASE_DIR = settings.BASE_DIR
full_pdf_path = os.path.join(BASE_DIR, "./docs/download-1.pdf")

with pdfplumber.open(full_pdf_path) as pdf:
    for page in pdf.pages:
        print(page.extract_tables())
