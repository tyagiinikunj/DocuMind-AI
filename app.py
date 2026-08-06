import streamlit as st
import time
import io
import re 

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

if "messages" not in st.session_state:
    st.session_state.messages = []

def stream_text(text):
    tokens = re.split(r'(\s+)',text)
    for token in tokens:
        yield token
        time.sleep(0.02)

with st.sidebar:

    st.title("📄 DocuMind AI")

    st.divider()

    st.markdown("### 🤖 Tech Stack")

    st.write("**LLM:** Llama 3.1 8B")
    st.write("**Embeddings:** MiniLM")
    st.write("**Vector DB:** FAISS")

    st.divider()

    if st.button("🗑 Clear Chat"):
        st.session_state.messages =[]
        st.rerun()
    st.divider()

    chat_history = ""

    for message in st.session_state.get("messages",[]):

        role = message["role"].capitalize()

        chat_history += f"{role}:\n"

        chat_history += message["content"]

        chat_history += "\n\n"

    st.download_button(
    label="📥 Download Chat",
    data=chat_history,
    file_name="chat_history.txt",
    mime="text/plain"
)


    st.divider()

    st.caption("Made with ❤️ using LangChain + Groq")

st.title("📄 DocuMind AI")
st.subheader("Chat with your PDF using AI")



uploaded_file = st.file_uploader(
    "Upload your PDF",
    type=["pdf"]
)

current_file = uploaded_file.name if uploaded_file else None

for message in st.session_state.get("messages",[]):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if uploaded_file:
    if(
    
     "rag_ready" not in st.session_state or st.session_state.get("current_file")!= current_file
    ):
        
        

        docs = load_pdf(uploaded_file)

        chunks = split_documents(docs)

        vector_store = create_vector_store(chunks)

        retriever = get_retriever(vector_store)

        llm = load_llm()

        st.session_state.retriever = retriever
        st.session_state.llm = llm
        st.session_state.rag_ready = True

        st.session_state.current_file = current_file
        st.session_state.messages = []

    retriever = st.session_state.retriever
    llm = st.session_state.llm

    prompt = ChatPromptTemplate.from_template(
    """
    You are an AI assistant that answers questions using the uploaded PDF.

    Use the previous conversation whenever it is relevant.

    If the user asks follow-up questions like:
    - Explain more
    - Give an example
    - Summarize it
    - Tell me more
    - Why?
    - How?

    then use the previous conversation together with the PDF context.

    Answer ONLY from the uploaded PDF.

    If the answer is not present in the context, reply exactly:

    "I couldn't find that information in the uploaded PDF."

    Format your answer using Markdown.

    Previous Conversation:
    {chat_history}

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

        with st.spinner("Searching your PDF....."):
            chat_history = ""

            for msg in st.session_state.messages:
                chat_history += f"{msg['role']}: {msg['content']}\n"

            response = rag_chain.invoke(
            {
                    "input": question,
                     "chat_history": chat_history
            }
            )

        answer = response["answer"]
        source_documents = response["context"]

        

        with st.chat_message("assistant"):

         streamed_answer = st.write_stream(stream_text(answer))

        st.markdown("---")
        st.markdown("### 📄 Sources")

        st.session_state.messages.append(
            {
                "role" : "assistant",
                "content" : streamed_answer 
            }
        )

        pages = set()

        for doc in source_documents:

            if "page" in doc.metadata:
                pages.add(doc.metadata["page"] + 1)

        if pages:
            st.write(", ".join(f"Page {page}" for page in sorted(pages)))