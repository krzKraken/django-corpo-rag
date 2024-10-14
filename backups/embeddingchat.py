#!/usr/bin/env python3
import os

import openai
from dotenv import load_dotenv
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from termcolor import colored

from corpo_chatbot.settings import BASE_DIR

# from src.response_to_html import format_to_html
# from src.token_calculator import main

# loading dotenv
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_tokens=1000)
chromadb_path = os.path.join(BASE_DIR, "vectordb")
chroma_local = Chroma(
    persist_directory=chromadb_path,
    embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"),
)


def prompt(text):
    system_prompt = text + "{context}"
    print(colored(f"########...ESTO ES UNA PRUEBA.############\n"))
    print(colored(system_prompt, "red"))

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )

    print(colored(f"########...ESTO ES UNA PRUEBA.############\n"))
    return prompt


def complete_query(query, llm, chroma_db, prompt):
    retriever = chroma_db.as_retriever()
    chain = create_stuff_documents_chain(llm, prompt)
    rag = create_retrieval_chain(retriever, chain)

    # Obtener el resultado de la consulta
    retrieved_documents = retriever.invoke(query)

    combined_content = ""
    if retrieved_documents:
        for i, doc in enumerate(retrieved_documents):
            # Obtener el ID del documento actual
            doc_id = doc.metadata.get("id", "ID no disponible")
            print(colored(f"########...DOCUMENT ID: {doc_id}...############", "yellow"))

            # Obtener el contenido de la página actual
            current_content = doc.page_content

            # Agregar el contenido de la página actual al contenido combinado
            combined_content += current_content + "\n\n"

            # Obtener la siguiente página si existe
            next_page_id = (
                int(doc_id) + 1
            )  # Asumiendo que los IDs son números consecutivos
            next_page_result = chroma_db.get(where={"id": next_page_id})

            # Si la siguiente página existe, agregar su contenido
            if next_page_result and len(next_page_result) > 0:
                next_page_content = next_page_result[0].page_content
                combined_content += next_page_content + "\n\n"

            # Romper después de la primera iteración ya que estamos buscando solo la primera coincidencia
            break

    # Crear la cadena de recuperación y generación de respuesta con el contenido combinado
    rag_results = rag.invoke({"input": query, "context": combined_content})

    # Imprimir el contexto combinado para verificar
    print(
        colored(f"########...RETRIEVER CON CONTENIDO EXTENDIDO.############\n", "green")
    )
    print(colored(combined_content, "blue"))
    print(
        colored(f"########...RETRIEVER CON CONTENIDO EXTENDIDO.############\n", "green")
    )

    return rag_results


text = """Eres un asistente experto que responde preguntas basadas en los documentos relevantes.Por favor, responde a mi pregunta basándote en estos documentos. Al final de cada respuesta menciona el origen del documento (nombre de documento) y página donde se encuentra. Si no sabes la respuesta solo di que no tienes informacion de este documento"""


def get_embedding_response(question):
    try:
        response = complete_query(question, llm, chroma_local, prompt(text))["answer"]
        print(colored(f"\n[+] Response: {response}", "blue"))
        return response
    except Exception as e:
        print(colored(f"Error: {e}", "red"))
        return "No fue posible conectar con la base de datos de embeddings"
