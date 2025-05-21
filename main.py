import sys
import asyncio
import subprocess

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import streamlit as st
import parser, embeddings,chain
import tempfile
from pathlib import Path
import requests
import re
import browser_user


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
    
def run_async_func(coro):
    try:
        return asyncio.run(coro)
    except RuntimeError as e:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro)

def get_pdf_url_from_keyword(keyword):
    result = subprocess.run(
        [sys.executable, "browser_user.py", keyword],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        url = result.stdout.strip()
        print("URL:", url) 
        return url
    else:
        st.error(f"Error running browser_user.py: {result.stderr}")
        return None

method = st.radio("Choose input method", ["Upload PDF", "Enter URL","Download paper via keyword."], key="input_method")

# Reset session state if the input method changes
if "last_radio" not in st.session_state:
    st.session_state.last_radio = method
if method != st.session_state.last_radio:
    for key in ["pdf_path", "last_keyword"]:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.last_radio = method

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

elif method == "Download paper via keyword.":
    keyword = st.text_input("Enter a keyword to search for papers")
    if "last_keyword" not in st.session_state:
        st.session_state.last_keyword = ""
    if "pdf_path" not in st.session_state:
        st.session_state.pdf_path = None

    if keyword and (keyword != st.session_state.last_keyword or st.session_state.pdf_path is None):
        with st.spinner("Searching for papers..."):
            url = get_pdf_url_from_keyword(keyword)
            if url:
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        download_pdf_from_url(url, Path(tmp.name))
                        st.session_state.pdf_path = Path(tmp.name)
                        st.session_state.last_keyword = keyword
                    st.success("PDF downloaded successfully!")
                except Exception as e:
                    st.error(f"Failed to download PDF: {e}")
            else:
                st.error("No arXiv PDF link found.")

    pdf_path = st.session_state.pdf_path

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
                    result = qa_chain.invoke({"query": question})
                    st.markdown("### Answer")
                    cleaned_result = re.sub(r"<think>.*?</think>", "", result["result"], flags=re.DOTALL).strip()
                    st.write(cleaned_result)

                    st.markdown("### Sources")
                    for doc in result["source_documents"]:
                        st.markdown(f"Page {doc.metadata['page']}: {doc.page_content[:300]}...")