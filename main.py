import streamlit as st
import parser
import tempfile
from pathlib import Path

st.set_page_config(page_title="Research Copilot", layout="centered")
st.title("📄 Research Copilot: PDF Reader")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
if uploaded_file is not None:
    with st.spinner("Processing..."):
        # print(uploaded_file.name)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:#creating temp file so that the path is given fully
            tmp.write(uploaded_file.read())
            tmp_path = Path(tmp.name)
        full_text, page_texts, metadata = parser.extract_text_from_pdf(tmp_path,uploaded_file.name)
        chunks = parser.chunk_pages_with_metadata(page_texts)

        # st.subheader("Extracted Text")
        st.subheader("Metadata")
        st.json(metadata)

        st.subheader(f"Total Chunks: {len(chunks)}")
        for c in chunks[:3]:#show first 3 chunks
            st.markdown(f"**Page {c['page']}**:")
            st.write(c['text'])

        # question = st.text_input("Ask a question about the text:")
        # if question:
        #     with st.spinner("Generating answer..."):
        #         answer = parser.answer_question(pdf_text, question)
        #         st.subheader("Answer")
        #         st.write(answer)

