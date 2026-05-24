import os
import streamlit as st

from pypdf import PdfReader

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

from langchain_community.vectorstores import FAISS

from langchain_huggingface import (
    HuggingFaceEmbeddings
)

from langchain_mistralai import (
    ChatMistralAI
)

# ─────────────────────────────────────────────────────────────
# EMBEDDINGS
# ─────────────────────────────────────────────────────────────

@st.cache_resource
def load_embeddings():

    return HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5"
    )

# ─────────────────────────────────────────────────────────────
# LOAD LLM ONCE
# ─────────────────────────────────────────────────────────────

@st.cache_resource
def load_llm():

    return ChatMistralAI(
        model="ministral-3b-latest",
        temperature=0.2,
        mistral_api_key=os.getenv(
            "MISTRAL_API_KEY"
        )
    )

# ─────────────────────────────────────────────────────────────
# EXTRACT PDF TEXT
# ─────────────────────────────────────────────────────────────

def get_pdf_text(pdf_docs):

    text_parts = []

    for pdf in pdf_docs:

        pdf_reader = PdfReader(pdf)

        for page in pdf_reader.pages:

            extracted_text = page.extract_text()

            if extracted_text:

                text_parts.append(extracted_text)

    return "\n".join(text_parts)

# ─────────────────────────────────────────────────────────────
# SPLIT TEXT
# ─────────────────────────────────────────────────────────────

def get_text_chunks(text):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    return splitter.split_text(text)

# ─────────────────────────────────────────────────────────────
# VECTOR STORE
# ─────────────────────────────────────────────────────────────

def get_vector_store(text_chunks):

    embeddings = load_embeddings()

    vector_store = FAISS.from_texts(
        text_chunks,
        embedding=embeddings
    )

    # STORE ONLY IN MEMORY
    st.session_state.vector_store = (
        vector_store
    )

# ─────────────────────────────────────────────────────────────
# PDF CHAT RESPONSE
# ─────────────────────────────────────────────────────────────

def user_input(user_question):

    if "vector_store" not in st.session_state:

        return (
            "❌ Please upload and process PDFs first."
        )

    docs = (
        st.session_state.vector_store
        .similarity_search(
            user_question,
            k=3
        )
    )

    # SHORTER CONTEXT
    conversation_context = ""

    if "pdf_conversation" in st.session_state:

        recent_messages = (
            st.session_state
            .pdf_conversation[-4:]
        )

        for msg in recent_messages:

            conversation_context += (
                f"{msg['role']}: "
                f"{msg['content']}\n"
            )

    docs_text = "\n\n".join(
        [
            doc.page_content
            for doc in docs
        ]
    )

    final_prompt = f"""
    Answer using the PDF context.

    Previous conversation:
    {conversation_context}

    PDF context:
    {docs_text}

    Question:
    {user_question}
    """

    llm = load_llm()

    try:

        response = llm.invoke(
            final_prompt
        )

        return response.content

    except Exception as e:

        return f"❌ Error: {str(e)}"