from langchain_community.document_loaders import PyPDFLoader
import os


def load_pdf(uploaded_file):
    """
    Save uploaded PDF and load it using LangChain.
    """

    os.makedirs("uploads", exist_ok=True)

    file_path = os.path.join("uploads", uploaded_file.name)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    loader = PyPDFLoader(file_path)

    documents = loader.load()

    return documents