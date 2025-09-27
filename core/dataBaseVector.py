import os
import hashlib
from typing import List

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

from langchain_community.document_loaders import DirectoryLoader, PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

DATA_PATH = os.path.join(os.path.dirname(__file__), "files")
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")
EMBED_MODEL = "mxbai-embed-large"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100


def load_documents_md():
    loader = DirectoryLoader(DATA_PATH, glob="*.md")
    documents = loader.load()
    print(f"Loaded {len(documents)} Markdown documents.")
    return documents

def load_documents_pdf():
    loader = PyPDFDirectoryLoader(DATA_PATH)
    documents = loader.load()
    print(f"Loaded {len(documents)} PDF documents.")
    return documents

def load_all_documents():
    md_docs = load_documents_md()
    pdf_docs = load_documents_pdf()
    print(f"Total documents loaded: {len(md_docs) + len(pdf_docs)}")
    return md_docs + pdf_docs

def divide_documents_in_chunks(documents, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        length_function=len,
        is_separator_regex=True,
    )
    chunks = text_splitter.split_documents(documents)
    
    # Print detalhado dos chunks
    print("\n=== CHUNKS ANALYSIS ===")
    for i, chunk in enumerate(chunks):
        print(f"\n--- Chunk {i+1} ---")
        print(f"Source: {chunk.metadata.get('source', 'Unknown')}")
        print(f"Page: {chunk.metadata.get('page', 'N/A')}")
        print(f"Length: {len(chunk.page_content)} characters")
        print(f"Preview: {chunk.page_content[:150]}...")
        if len(chunk.page_content) > 150:
            print(f"...{chunk.page_content[-50:]}")  # Últimos 50 caracteres
    
    print("\n=== SUMMARY ===")
    print(f"Total chunks created: {len(chunks)}")
    
    # Estatísticas dos chunks
    lengths = [len(chunk.page_content) for chunk in chunks]
    print(f"Average chunk size: {sum(lengths) / len(lengths):.0f} characters")
    print(f"Min chunk size: {min(lengths)} characters")
    print(f"Max chunk size: {max(lengths)} characters")
    
    return chunks

def get_embedding_function():
    embeddings = OllamaEmbeddings(
        model=EMBED_MODEL, 
        base_url="http://192.168.0.26:11434"
        )
    return embeddings

def add_to_chroma(chunks: List[Document]):
    print(f"Starting to add {len(chunks)} chunks to ChromaDB...")

    db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=get_embedding_function()
    )

    ids_chunks = [hashlib.sha256(doc.page_content.encode()).hexdigest() for doc in chunks]

    existing_items_ids = db.get(include=[])
    existing_ids = set(existing_items_ids["ids"])
    print(f"Found {len(existing_ids)} existing documents in database.")

    chunks_to_add = []
    ids_to_add = []

    for i, chunk_id in enumerate(ids_chunks):
        if chunk_id not in existing_ids:
            chunks_to_add.append(chunks[i])
            ids_to_add.append(chunk_id)

    # 5. Adiciona os novos chunks, se houver algum
    if len(chunks_to_add) > 0:
        print(f"Adding {len(chunks_to_add)} new chunks to database...")
        db.add_documents(
            documents=chunks_to_add,
            ids=ids_to_add
        )
        print("New chunks added and saved successfully.")
    else:
        print("No new chunks to add. Database is already up to date.")
