import streamlit as st

from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

from utils.pdf_loader import load_pdf
from utils.text_splitter import split_documents
from utils.vector_store import create_vector_store
from utils.retriever import get_retriever
from utils.llm import load_llm


st.set_page_config(
    page_title="DocuMind AI",
    page_icon="📄",
    layout="wide"
)

st.title("📄 DocuMind AI")
st.subheader("Chat with your PDF using AI")

uploaded_file = st.file_uploader(
    "Upload your PDF",
    type=["pdf"]
)

if uploaded_file:

    docs = load_pdf(uploaded_file)

    chunks = split_documents(docs)

    vector_store = create_vector_store(chunks)

    retriever = get_retriever(vector_store)

    llm = load_llm()

    prompt = ChatPromptTemplate.from_template(
        """
You are an AI assistant.

Answer ONLY using the provided context.

If the answer is not present in the context, reply:

"I couldn't find that information in the uploaded PDF."

Context:
{context}

Question:
{input}
"""
    )

    document_chain = create_stuff_documents_chain(
        llm,
        prompt
    )

    rag_chain = create_retrieval_chain(
        retriever,
        document_chain
    )

    st.success("✅ PDF Ready!")

    question = st.text_input(
        "Ask anything about the PDF"
    )

    if question:

        response = rag_chain.invoke(
            {
                "input": question
            }
        )

        st.markdown("## Answer")

        st.write(response["answer"])