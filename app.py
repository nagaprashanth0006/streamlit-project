import os
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain.chains import ConversationalRetrievalChain

OLLAMA_BASE_URL = "http://ollama:11434"
MODEL_NAME = "llama3.2:latest"
PDF_DIRECTORY = "./pdfs"
DB_DIRECTORY = "./chroma_db"

st.set_page_config(page_title="RAG-KB", layout="wide")
st.title("📚 RAG-KB with Ollama & PDFs")


@st.cache_resource
def load_and_process_pdfs(directory):
    if not os.path.exists(directory) or not any(
        file.endswith(".pdf") for file in os.listdir(directory)
    ):
        return []
    pdf_files = [
        os.path.join(directory, file)
        for file in os.listdir(directory)
        if file.endswith(".pdf")
    ]
    documents = []
    for pdf_file in pdf_files:
        loader = PyPDFLoader(pdf_file)
        documents.extend(loader.load())
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = text_splitter.split_documents(documents)
    return [doc for doc in split_docs if doc.page_content.strip()]


@st.cache_resource
def init_db(documents):
    embeddings = OllamaEmbeddings(base_url=OLLAMA_BASE_URL, model=MODEL_NAME)
    vectordb = Chroma.from_documents(
        documents, embeddings, persist_directory=DB_DIRECTORY
    )
    vectordb.persist()
    return vectordb


@st.cache_resource
def init_chain(vectordb):
    llm = Ollama(base_url=OLLAMA_BASE_URL, model=MODEL_NAME)
    retriever = vectordb.as_retriever(search_kwargs={"k": 5})
    return ConversationalRetrievalChain.from_llm(llm, retriever=retriever)


embeddings = OllamaEmbeddings(base_url=OLLAMA_BASE_URL, model=MODEL_NAME)
test_embed = embeddings.embed_query("test embedding")
if not test_embed:
    st.error(
        "Embeddings are not working correctly. Check Ollama connectivity and model."
    )

documents = load_and_process_pdfs(PDF_DIRECTORY)

if documents:
    vectordb = init_db(documents)
    qa_chain = init_chain(vectordb)
else:
    qa_chain = None

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []


def chat_with_ollama(question):
    if qa_chain:
        response = qa_chain.invoke(
            {"question": question, "chat_history": st.session_state["chat_history"]}
        )
    else:
        llm = Ollama(base_url=OLLAMA_BASE_URL, model=MODEL_NAME)
        response = {"answer": llm.invoke(question)}
    st.session_state["chat_history"].append((question, response["answer"]))
    return response["answer"]


user_input = st.chat_input("Ask your question...")

if st.session_state["chat_history"]:
    for user_q, ai_response in st.session_state["chat_history"]:
        with st.chat_message("user"):
            st.markdown(user_q)
        with st.chat_message("assistant"):
            st.markdown(ai_response)

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    with st.chat_message("assistant"):
        response = chat_with_ollama(user_input)
        st.markdown(response)
