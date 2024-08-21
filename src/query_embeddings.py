import os

import openai
from dotenv import load_dotenv
from langchain.vectorstores import Chroma

# Cargar las variables del archivo .env
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

VECTOR_DB_PATH = "vectordb/"


def search_and_respond(query_text, top_k=5):
    """Buscar los documentos más relevantes y generar una respuesta en lenguaje natural"""
    # Conectar con ChromaDB y cargar la colección de embeddings
    client = Chroma(persist_directory=VECTOR_DB_PATH)

    # Generar el embedding de la consulta usando OpenAI
    embedding_response = openai.embeddings.create(
        input=query_text, model="text-embedding-ada-002"
    )
    query_embedding = embedding_response["data"][0]["embedding"]

    # Realizar la búsqueda de los embeddings más similares
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,  # Número de resultados más cercanos que deseas
    )

    # Obtener el contenido de los documentos más relevantes
    relevant_docs = results["documents"][0]

    # Unir el contenido de los documentos relevantes en un solo texto
    combined_docs = "\n\n".join(relevant_docs)

    # Llamada a la API de OpenAI para generar la respuesta en lenguaje natural
    response = openai.ChatCompletion.create(
        model="gpt-4",  # O "gpt-3.5-turbo" si prefieres
        messages=[
            {
                "role": "system",
                "content": "Eres un asistente experto que responde preguntas basadas en los documentos relevantes.",
            },
            {"role": "user", "content": query_text},
            {
                "role": "assistant",
                "content": f"Los siguientes documentos relevantes están disponibles:\n\n{combined_docs}",
            },
            {
                "role": "user",
                "content": "Por favor, responde a mi pregunta basándote en estos documentos.",
            },
        ],
    )

    # Imprimir la respuesta generada
    answer = response["choices"][0]["message"]["content"]
    print(f"Respuesta:\n{answer}")


# Ejemplo de uso
if __name__ == "__main__":
    query = input("Ingrese su consulta: ")
    search_and_respond(query)
