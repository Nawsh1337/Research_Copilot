import streamlit as st
import parser, embeddings,chain
import tempfile
from pathlib import Path
import requests
import re

st.set_page_config(page_title="Research Copilot", layout="centered")
st.title("📄 Research Copilot: PDF Reader")

def download_pdf_from_url(url: str, output_path: Path):
    if "arxiv.org" in url:
        paper_id = url.strip().split("/")[-1]
        pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"
    else:
        pdf_url = url

    r = requests.get(pdf_url)
    if r.status_code == 200 and "application/pdf" in r.headers.get("Content-Type", ""):
        with open(output_path, "wb") as f:
            f.write(r.content)
        return output_path
    else:
        raise ValueError("Could not download PDF. Check the URL or site support.")
    
method = st.radio("Choose input method", ["Upload PDF", "Enter URL"])#either upload pdf or enter url of paper

pdf_path = None

if method == "Upload PDF":
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            pdf_path = Path(tmp.name)

elif method == "Enter URL":
    url = st.text_input("Paste paper URL")
    if url:
        with st.spinner("Downloading PDF..."):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    download_pdf_from_url(url, Path(tmp.name))
                    pdf_path = Path(tmp.name)
                st.success("PDF downloaded successfully!")
            except Exception as e:
                st.error(f"Failed to download PDF: {e}")

if pdf_path:
    with st.spinner("Processing..."):
        parsed = parser.extract_text_from_pdf(pdf_path,pdf_path.name)
        chunks = parser.chunk_pages_with_metadata(parsed["page_texts"])
        st.subheader("Metadata")
        st.json(parsed['metadata'])
        # st.subheader("First Few Chunks")
        # for c in chunks[:3]:
            # st.markdown(f"**Page {c['page']}**")
            # st.write(c['text'])
        if chunks:
            vectordb = embeddings.embed_chunks_faiss(chunks)
            qa_chain = chain.build_qa_chain(vectordb)

            question = st.text_input("Ask a question about the paper:")
            if question:
                with st.spinner("Generating answer..."):
                    result = qa_chain({"query": question})
                    st.markdown("### Answer")
                    cleaned_result = re.sub(r"<think>.*?</think>", "", result["result"], flags=re.DOTALL).strip()
                    st.write(cleaned_result)

                    st.markdown("### Sources")
                    for doc in result["source_documents"]:
                        st.markdown(f"Page {doc.metadata['page']}: {doc.page_content[:300]}...")