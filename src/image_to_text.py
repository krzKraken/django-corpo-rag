#!/usr/bin/env python

import os

import pytesseract
from PIL import Image

from corpo_chatbot.settings import BASE_DIR

# function for  convert images to text.


def get_images_from_pdf(pdf_name):
    pass


def image_to_text(image_file):
    path = os.path.join(BASE_DIR, f"images/{image_file}")

    # image = Image.open(image_path)
    # texto = pytesseract.image_to_string(image)
    # print(texto)
    return path
