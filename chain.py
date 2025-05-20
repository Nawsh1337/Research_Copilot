from langchain_groq.chat_models import ChatGroq
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
import os

load_dotenv()
def build_qa_chain(vectordb):
    retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": 4})
    llm = ChatGroq(model="qwen-qwq-32b", temperature=0.2)

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )
    return chain