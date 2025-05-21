
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


def embed_chunks_faiss(chunks):
    texts = [chunk["text"] for chunk in chunks]
    metadatas = [{"page": chunk["page"]} for chunk in chunks]

    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectordb = FAISS.from_texts(texts=texts, embedding=embedding, metadatas=metadatas)
    
    return vectordb
