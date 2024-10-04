from io import BytesIO

import fitz  # PyMuPDF
import pytesseract
from PIL import Image


def extract_text_from_pdf_with_images(pdf_path):
    # Abrir el archivo PDF
    doc = fitz.open(pdf_path)
    pages_content = []

    # Iterar sobre cada página del documento
    for page_number in range(doc.page_count):
        page = doc.load_page(page_number)
        text = page.get_text("text")  # Extrae el texto de la página

        # Extraer imágenes de la página
        images = page.get_images(full=True)
        image_text = ""

        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            # Convertir imagen a texto usando pytesseract
            image = Image.open(BytesIO(image_bytes))
            extracted_text = pytesseract.image_to_string(image)
            image_text += f"\nImagen {img_index + 1}: {extracted_text}"

        # Combinar el texto de la página con el texto extraído de las imágenes
        combined_text = text + image_text
        pages_content.append({"page_number": page_number + 1, "content": combined_text})

    return pages_content


# Ejemplo de uso
""" pdf_path = "ruta/al/archivo.pdf"
pages_content = extract_text_from_pdf_with_images(pdf_path)

# Mostrar el contenido extraído por página
for page in pages_content:
    print(f"Contenido de la página {page['page_number']}:\n")
    print(page['content'])
    print("-" * 50)
 """
