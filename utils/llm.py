import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Force load .env from project root
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env", override=True)

print("Loaded API:", os.getenv("GROQ_API_KEY"))

def load_llm():
    return ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0,
    )