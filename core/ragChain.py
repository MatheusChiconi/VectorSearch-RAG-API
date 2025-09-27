from . import dataBaseVector
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.chat_models import ChatOllama

PROMPT_TEMPLATE = """
Você é um assistente de IA prestativo e factual. 
Sua tarefa é responder à pergunta do usuário baseando-se estritamente no contexto fornecido abaixo.

CONTEXTO:
{context}

Se a informação necessária para responder à pergunta não estiver contida no contexto, responda exatamente com: 
"Desculpe, não encontrei informações sobre isso nos meus documentos." 
Não tente inventar uma resposta.
---

PERGUNTA: {question}
"""
MODEL = "llama3.1:8b-instruct-q4_K_M"
NUM_CHUNKS = 10

def load_database():
    db = Chroma(
        persist_directory=dataBaseVector.CHROMA_PATH,
        embedding_function=dataBaseVector.get_embedding_function()
    )
    return db

def retrieve_context(question: str) -> str:
    db = load_database()
    results = db.similarity_search_with_score(question, NUM_CHUNKS)
    context = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    return context

def format_prompt(question: str, context: str) -> str:
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(question=question, context=context)
    return prompt

def load_model():
    model = ChatOllama(
        model=MODEL,
        base_url="http://192.168.0.26:11434"
    )
    return model

def get_answer(question: str) -> str:
    context = retrieve_context(question)
    prompt = format_prompt(question, context)
    print("Prompt formatado:\n", prompt)
    model = load_model()
    print("Modelo carregado:", model)
    response_text = model.invoke(prompt)
    return response_text
