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
if "messages" not in st.session_state:
    st.session_state.messages = []

uploaded_file = st.file_uploader(
    "Upload your PDF",
    type=["pdf"]
)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if uploaded_file:
    if "rag_ready" not in st.session_state:

        docs = load_pdf(uploaded_file)

        chunks = split_documents(docs)

        vector_store = create_vector_store(chunks)

        retriever = get_retriever(vector_store)

        llm = load_llm()

        st.session_state.retriever = retriever
        st.session_state.llm = llm
        st.session_state.rag_ready = True

    retriever = st.session_state.retriever
    llm = st.session_state.llm

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

    question = st.chat_input("Ask anything about the PDF")

    if question:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )

        with st.chat_message("user"):
            st.markdown(question)

        response = rag_chain.invoke(
            {
                "input": question
            }
        )

        answer = response["answer"]
        source_documents = response["context"]

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        with st.chat_message("assistant"):

         st.markdown(answer)

        st.markdown("---")
        st.markdown("### 📄 Sources")

        pages = set()

        for doc in source_documents:

            if "page" in doc.metadata:
                pages.add(doc.metadata["page"] + 1)

        if pages:
            st.write(", ".join(f"Page {page}" for page in sorted(pages)))