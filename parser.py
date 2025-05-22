from langchain.text_splitter import RecursiveCharacterTextSplitter
import fitz #PyMuPDF
from pathlib import Path

def extract_text_from_pdf(pdf_path,file_name):
    doc = fitz.open(str(pdf_path))
    page_texts = []

    for page in doc:
        page_texts.append(page.get_text())
    full_text = "\n\n".join(page_texts)
    metadata = {
        "file_name": file_name,
        "num_pages": len(doc),
    }

    doc.close()
    return {
        "full_text": full_text,
        "page_texts": page_texts,
        "metadata": metadata
    }

def chunk_pages_with_metadata(page_texts):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = []

    for i, page_text in enumerate(page_texts, start=1):
        page_chunks = splitter.split_text(page_text)
        for chunk in page_chunks:
            chunks.append({
                "page": i,
                "text": chunk
            })

    return chunks