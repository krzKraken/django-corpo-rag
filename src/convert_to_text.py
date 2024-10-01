import os

import pytesseract
from pdf2image import convert_from_path
from PIL import Image

# Crea la carpeta img si no existe
if not os.path.exists("img"):
    os.makedirs("img")

# Configura la ruta de tesseract si es necesario
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def extraer_imagenes_y_convertir_a_texto(pdf_path):
    # Convertir las páginas del PDF a imágenes
    pages = convert_from_path(pdf_path)

    for i, page in enumerate(pages):
        # Guardar la imagen de la página en la carpeta img
        image_path = f"img/page_{i+1}.jpg"
        page.save(image_path, "JPEG")

        # Aplicar OCR a la imagen
        texto_imagen = pytesseract.image_to_string(
            Image.open(image_path), lang="eng"
        )  # Cambia 'eng' por el idioma necesario

        # Imprimir el texto extraído solo de las imágenes
        if texto_imagen.strip():  # Verifica que haya texto extraído
            print(f"Texto extraído de las imágenes en la página {i+1}:")
            print(texto_imagen)
            print("-" * 50)
        else:
            print(f"No se detectó texto en las imágenes de la página {i+1}")

    # Eliminar las imágenes después de procesarlas
    eliminar_imagenes_temporales("img")


def eliminar_imagenes_temporales(carpeta):
    for archivo in os.listdir(carpeta):
        archivo_path = os.path.join(carpeta, archivo)
        try:
            if os.path.isfile(archivo_path):
                os.unlink(archivo_path)  # Elimina el archivo
        except Exception as e:
            print(f"Error al eliminar {archivo_path}: {e}")


extraer_imagenes_y_convertir_a_texto("./test_imagenes_texto_corto.pdf")
