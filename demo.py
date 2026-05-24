import streamlit as st
import time
import os
from title_generator import generate_chat_title
from concurrent.futures import ThreadPoolExecutor
from supabase_client import supabase
from dotenv import load_dotenv
from pypdf import PdfReader
from streamlit_mic_recorder import mic_recorder
from voice_utils import transcribe_audio

# ─────────────────────────────────────────────────────────────
# LANGCHAIN IMPORTS
# ─────────────────────────────────────────────────────────────

from agents import (
    build_reader_agent,
    build_search_agent,
    writer_chain,
    critic_chain
)

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_mistralai import ChatMistralAI


from memory_db import (
    init_db,
    save_chat,
    update_chat,
    get_all_chats,
    get_chat,
    delete_chat,
    rename_chat
)


# ─────────────────────────────────────────────────────────────
# ENV SETUP
# ─────────────────────────────────────────────────────────────

load_dotenv()

init_db()

if not os.getenv("MISTRAL_API_KEY"):
    st.error("❌ MISTRAL_API_KEY not found in .env file")
    st.stop()


# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="ResearchMind",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #e8e4dc;
}

.stApp {
    background: #0a0a0f;
    background-image:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(255,140,50,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 110%, rgba(255,80,30,0.08) 0%, transparent 55%);
}

#MainMenu, footer, header {
    visibility: hidden;
}

.block-container {
    padding: 2rem 3rem 4rem;
    max-width: 1200px;
}

.hero {
    text-align: center;
    padding: 3rem 0;
}

.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: 4rem;
    color: #f0ebe0;
}

.hero h1 span {
    color: #ff8c32;
}

.hero-sub {
    color: #a09890;
    font-size: 1rem;
    max-width: 600px;
    margin: auto;
    line-height: 1.6;
}

.input-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,140,50,0.15);
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 2rem;
}

.stTextInput input {
    background: rgba(255,255,255,0.05) !important;
    color: white !important;
    border-radius: 10px !important;
}

.stButton button {
    background: linear-gradient(135deg, #ff8c32 0%, #ff5a1a 100%) !important;
    color: black !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: bold !important;
    width: 100%;
}

.report-panel {
    background: rgba(255,255,255,0.03);
    border-radius: 14px;
    padding: 2rem;
    margin-top: 1rem;
}

.notice {
    text-align: center;
    margin-top: 3rem;
    color: #777;
    font-size: 0.8rem;
}

.pipeline-card {
    padding: 18px;
    border-radius: 14px;
    margin-bottom: 14px;
    font-weight: 600;
    border: 1px solid rgba(255,255,255,0.08);
    transition: 0.3s;
    font-size: 16px;
}

.waiting {
    background: rgba(255,255,255,0.03);
    color: #888;
}

.running {
    background: rgba(255,140,50,0.15);
    border: 1px solid #ff8c32;
    color: white;
    box-shadow: 0 0 20px rgba(255,140,50,0.25);
}
            
.chat-container {
    margin-top: 2rem;
}

.user-msg {
    background: linear-gradient(135deg, #ff8c32 0%, #ff5a1a 100%);
    color: black;
    padding: 14px 18px;
    border-radius: 18px;
    margin: 10px 0;
    margin-left: 25%;
    font-weight: 500;
}

.ai-msg {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    padding: 16px 18px;
    border-radius: 18px;
    margin: 10px 0;
    margin-right: 25%;
    color: white;
}

.done {
    background: rgba(0,255,120,0.12);
    border: 1px solid #00c853;
    color: white;
}

</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────

if "results" not in st.session_state:
    st.session_state.results = {}

if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = ""

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

if "conversation" not in st.session_state:
    st.session_state.conversation = []

if "pdf_conversation" not in st.session_state:
    st.session_state.pdf_conversation = []

if "user" not in st.session_state:
    st.session_state.user = None

if "is_guest" not in st.session_state:
    st.session_state.is_guest = False

if "voice_text" not in st.session_state:
    st.session_state.voice_text = ""

if "followup_text" not in st.session_state:
    st.session_state.followup_text = ""

def get_user_email():

    if st.session_state.is_guest:
        return st.session_state.user["email"]

    return st.session_state.user.email

# ─────────────────────────────────────────────────────────────
# AUTHENTICATION
# ─────────────────────────────────────────────────────────────

if st.session_state.user is None:

    st.markdown("""
    <style>

.auth-container {
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
}

.auth-card {
    width: 460px;
    padding: 50px 40px;
    border-radius: 28px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,140,50,0.18);
    backdrop-filter: blur(18px);
    box-shadow: 0 0 60px rgba(255,140,50,0.12);
    display: flex;
    flex-direction: column;
    justify-content: center;
    margin: auto;
}

.auth-logo-box {
    height: 170px;
    border-radius: 24px;
    border: 1px solid rgba(255,140,50,0.18);

    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;

    margin-bottom: 30px;

    background: rgba(255,255,255,0.02);
}

.auth-title {
    text-align: center;
    font-size: 58px;
    font-weight: 800;
    color: white;
}

    .auth-sub {
        text-align: center;
        color: #aaa;
        margin-bottom: 35px;
        font-size: 15px;
    }

    .stTextInput input {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        color: white !important;
        border-radius: 12px !important;
        height: 50px !important;
    }

    .stButton button {
        height: 48px;
        border-radius: 12px !important;
        font-size: 15px !important;
        font-weight: 700 !important;
    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="auth-container">', unsafe_allow_html=True)

    st.markdown("""
    <div class="auth-card">

    <div class="auth-title">
        Research<span>Mind</span>
    </div>

    <div class="auth-sub">
        AI-powered research, analysis & PDF conversations
    </div>
    """, unsafe_allow_html=True)

    auth_mode = st.radio(
        "",
        ["Login", "Signup"],
        horizontal=True
    )

    email = st.text_input(
        "Email Address",
        placeholder="Enter your email"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password"
    )

    # SIGNUP

    if auth_mode == "Signup":

        if st.button(
            "✨ Create Account",
            use_container_width=True
        ):

            try:

                response = supabase.auth.sign_up({
                    "email": email,
                    "password": password
                })

                st.success(
                    "✅ Account created successfully! Please login."
                )

            except Exception as e:

                st.error(str(e))

    # LOGIN

    else:

        if st.button(
            "🚀 Login",
            use_container_width=True
        ):

            try:

                response = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })

                st.session_state.user = response.user

                st.success("✅ Login successful!")

                st.rerun()

            except Exception:

                st.error("Invalid email or password")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button(
        "👤 Continue as Guest",
        use_container_width=True
    ):

        st.session_state.user = {
            "email": "guest@researchmind.ai"
        }

        st.session_state.is_guest = True

        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    st.stop()
# ─────────────────────────────────────────────────────────────
# CACHED EMBEDDINGS (FASTER PDF PROCESSING)
# ─────────────────────────────────────────────────────────────

@st.cache_resource
def load_embeddings():

    return HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5"
    )

# ─────────────────────────────────────────────────────────────
# PDF FUNCTIONS
# ─────────────────────────────────────────────────────────────

def get_pdf_text(pdf_docs):

    text = ""

    for pdf in pdf_docs:

        pdf_reader = PdfReader(pdf)

        for page in pdf_reader.pages:

            extracted_text = page.extract_text()

            if extracted_text:
                text += extracted_text

    return text


def get_text_chunks(text):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100
    )

    return splitter.split_text(text)


def get_vector_store(text_chunks):

    embeddings = load_embeddings()

    vector_store = FAISS.from_texts(
        text_chunks,
        embedding=embeddings
    )

    vector_store.save_local("faiss_index")

    st.session_state.vector_store = vector_store


def user_input(user_question):

    # LOAD VECTOR STORE

    if "vector_store" not in st.session_state:

        if os.path.exists("faiss_index"):

            embeddings = load_embeddings()

            st.session_state.vector_store = FAISS.load_local(
                "faiss_index",
                embeddings,
                allow_dangerous_deserialization=True
            )

        else:

            return "❌ Please upload and process PDFs first."

    # SEARCH DOCUMENTS

    docs = st.session_state.vector_store.similarity_search(
        user_question,
        k=2
    )

    # BUILD PDF CHAT CONTEXT

    conversation_context = ""

    if "pdf_conversation" in st.session_state:

        recent_messages = st.session_state.pdf_conversation[-6:]

        for msg in recent_messages:

            role = msg["role"]
            content = msg["content"]

            conversation_context += f"{role}: {content}\n"

    # FAST MODEL

    llm = ChatMistralAI(
        model="ministral-3b-latest",
        temperature=0.2,
        mistral_api_key=os.getenv("MISTRAL_API_KEY")
    )

    # COMBINE DOCUMENT TEXT

    docs_text = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    # FINAL PROMPT

    final_prompt = f"""
    You are a helpful PDF assistant.

    Use the PDF context and previous conversation
    to answer naturally and accurately.

    PREVIOUS CONVERSATION:
    {conversation_context}

    PDF CONTEXT:
    {docs_text}

    USER QUESTION:
    {user_question}
    """

    # GENERATE RESPONSE

    response = llm.invoke(final_prompt)

    return response.content


# ─────────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────────



st.markdown("""
<div class="hero">
    <h1>Research<span>Mind</span></h1>

    
        Multi-Agent AI platform for deep research, intelligent analysis, and PDF conversations.

    
</div>
""", unsafe_allow_html=True)





# ─────────────────────────────────────────────────────────────
# SIDEBAR CHAT HISTORY
# ─────────────────────────────────────────────────────────────

with st.sidebar:

    st.markdown("# 🧠 ResearchMind")

    # USER STATUS

    if st.session_state.is_guest:

        st.warning("👤 Guest Mode")

    else:

        st.success(
            f"Logged in as {get_user_email()}"
        )

    # LOGOUT

    if st.button("🚪 Logout"):

        if not st.session_state.is_guest:
            supabase.auth.sign_out()

        st.session_state.user = None
        st.session_state.is_guest = False

        st.session_state.results = {}
        st.session_state.selected_topic = ""
        st.session_state.current_chat_id = None
        st.session_state.conversation = []
        st.session_state.pdf_conversation = []
        st.session_state.current_pdf_name = None

        st.rerun()

    # NEW CHAT

    if st.button("➕ New Chat", use_container_width=True):

        st.session_state.pdf_conversation = []
        st.session_state.current_pdf_name = None
        st.session_state.results = {}
        st.session_state.selected_topic = ""
        st.session_state.current_chat_id = None
        st.session_state.conversation = []

        st.rerun()

    # RECENT CHATS

    if not st.session_state.is_guest:

        st.markdown("### Recent Chats")

        all_chats = get_all_chats(
            get_user_email()
        )

    else:

        st.info(
            "Guest chats are temporary and won't be saved."
        )

        all_chats = []

    # CHAT LIST

    for chat in all_chats:

        chat_id = chat[0]
        title = chat[1]
        created = chat[2]

        with st.container():

            col1, col2, col3 = st.columns([6, 1, 1])

            # OPEN CHAT

            with col1:

                if st.button(
                    f"📝 {title}",
                    key=f"chat_{chat_id}",
                    use_container_width=True
                ):

                    selected_chat = get_chat(chat_id)

                    st.session_state.current_chat_id = chat_id

                    st.session_state.results = {
                        "search": selected_chat[4],
                        "reader": selected_chat[5],
                        "writer": selected_chat[6],
                        "critic": selected_chat[7]
                    }

                    st.session_state.selected_topic = selected_chat[3]

                    import json

                    saved_conversation = selected_chat[8]

                    try:

                        if (
                            saved_conversation
                            and saved_conversation.strip()
                        ):

                            loaded_conversation = json.loads(
                                saved_conversation
                            )

                            chat_type = (
                                selected_chat[10]
                                if len(selected_chat) > 10
                                else "web"
                            )

                            if chat_type == "pdf":

                                st.session_state.pdf_conversation = loaded_conversation
                                st.session_state.conversation = []

                            else:

                                st.session_state.conversation = loaded_conversation
                                st.session_state.pdf_conversation = []

                    except Exception:

                        st.session_state.conversation = []

                    st.rerun()

            # RENAME

            with col2:

                if st.button(
                    "✏️",
                    key=f"rename_{chat_id}"
                ):

                    st.session_state[
                        f"editing_{chat_id}"
                    ] = True

            # DELETE

            with col3:

                if st.button(
                    "🗑️",
                    key=f"delete_{chat_id}"
                ):

                    delete_chat(chat_id)

                    if (
                        st.session_state.current_chat_id
                        == chat_id
                    ):

                        st.session_state.results = {}
                        st.session_state.selected_topic = ""
                        st.session_state.current_chat_id = None
                        st.session_state.conversation = []
                        st.session_state.pdf_conversation = []

                    st.rerun()

            # RENAME INPUT

            if st.session_state.get(
                f"editing_{chat_id}",
                False
            ):

                new_title = st.text_input(
                    "New Title",
                    value=title,
                    key=f"title_input_{chat_id}"
                )

                save_col1, save_col2 = st.columns(2)

                with save_col1:

                    if st.button(
                        "Save",
                        key=f"save_{chat_id}"
                    ):

                        rename_chat(
                            chat_id,
                            new_title
                        )

                        st.session_state[
                            f"editing_{chat_id}"
                        ] = False

                        st.rerun()

                with save_col2:

                    if st.button(
                        "Cancel",
                        key=f"cancel_{chat_id}"
                    ):

                        st.session_state[
                            f"editing_{chat_id}"
                        ] = False

                        st.rerun()

# ─────────────────────────────────────────────────────────────
# TOP NAVIGATION TABS
# ─────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────
# ACTIVE PAGE STATE
# ─────────────────────────────────────────────────────────────

if "active_page" not in st.session_state:
    st.session_state.active_page = "🔬 AI Research"

# ─────────────────────────────────────────────────────────────
# PAGE NAVIGATION
# ─────────────────────────────────────────────────────────────

selected_page = st.radio(
    "",
    ["🔬 AI Research", "📘 PDF Chat"],
    horizontal=True,
    index=0 if st.session_state.active_page == "🔬 AI Research" else 1
)

st.session_state.active_page = selected_page

# ─────────────────────────────────────────────────────────────
# RESEARCH TAB
# ─────────────────────────────────────────────────────────────

if selected_page == "🔬 AI Research":

    left_col, right_col = st.columns([5, 4])

    with left_col:

        st.markdown(
            '<div class="input-card">',
            unsafe_allow_html=True
        )

        st.markdown("## 🔬 Research Assistant")

        st.markdown("### 🎤 Voice Research Input")

        audio = mic_recorder(
            start_prompt="🎙️ Start Recording",
            stop_prompt="🛑 Stop Recording",
            just_once=True,
            use_container_width=True
        )

        # TRANSCRIBE

        if audio:

            with st.spinner("Transcribing voice..."):

                transcript = transcribe_audio(
                    audio["bytes"]
                )

                st.session_state.voice_text = transcript

        # EDITABLE TEXT

        topic = st.text_area(
            "Research Topic",
            value=(
                st.session_state.voice_text
                or st.session_state.selected_topic
            ),
            placeholder="Speak or type your research topic...",
            height=120
        )

        run_btn = st.button(
            "⚡ Run Research Pipeline",
            use_container_width=True
        )

        st.markdown('</div>', unsafe_allow_html=True)

    with right_col:

        st.markdown("## 🔬 Pipeline")

        pipeline_placeholder = st.empty()


# ─────────────────────────────────────────────────────────────
# PDF CHAT TAB
# ─────────────────────────────────────────────────────────────

if selected_page == "📘 PDF Chat":

    st.markdown(
        '<div class="input-card">',
        unsafe_allow_html=True
    )

    st.markdown("## 📘 Chat With Your PDFs")

    # SESSION STATES

    if "pdf_conversation" not in st.session_state:
        st.session_state.pdf_conversation = []

    if "current_pdf_name" not in st.session_state:
        st.session_state.current_pdf_name = None

    # PDF UPLOAD

    pdf_docs = st.file_uploader(
        "Upload PDF Files",
        type=["pdf"],
        accept_multiple_files=True
    )

    process_pdf = st.button(
        "📄 Process PDFs",
        use_container_width=True
    )

    # PROCESS PDF

    if process_pdf:

        if pdf_docs:

            with st.spinner("Processing PDFs..."):

                raw_text = get_pdf_text(pdf_docs)

                text_chunks = get_text_chunks(raw_text)

                get_vector_store(text_chunks)

                # STORE PDF NAME
                pdf_names = [pdf.name for pdf in pdf_docs]

                st.session_state.current_pdf_name = ", ".join(pdf_names)

                st.success("✅ PDFs processed successfully!")

        else:

            st.warning("Please upload PDF files.")

    # DISPLAY CHAT HISTORY

    if st.session_state.pdf_conversation:

        st.markdown("## 💬 PDF Conversation")

        for msg in st.session_state.pdf_conversation:

            if msg["role"] == "user":

                st.markdown(
                    f"""
                    <div class="user-msg">
                        {msg["content"]}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    f"""
                    <div class="ai-msg">
                        {msg["content"]}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # SINGLE CHAT INPUT ONLY

    pdf_question = st.chat_input(
        "Ask anything from your PDF..."
    )

    # HANDLE PDF QUESTION

    if pdf_question:

        st.session_state.pdf_conversation.append({
            "role": "user",
            "content": pdf_question
        })

        with st.spinner("Searching PDF..."):

            response = user_input(pdf_question)

        st.session_state.pdf_conversation.append({
            "role": "assistant",
            "content": response
        })

        if not st.session_state.is_guest:

            if st.session_state.current_chat_id is None:

                save_chat(
                    user_email=get_user_email(),
                    title=st.session_state.current_pdf_name or "PDF Chat",
                    topic="PDF Conversation",
                    search_result="",
                    reader_result="",
                    writer_result=response,
                    critic_result="",
                    conversation=st.session_state.pdf_conversation,
                    pdf_name=st.session_state.current_pdf_name,
                    chat_type="pdf"
                )

                latest_chat = get_all_chats(
                    get_user_email()
                )[0]

                st.session_state.current_chat_id = latest_chat[0]

            else:

                update_chat(
                    chat_id=st.session_state.current_chat_id,
                    topic="PDF Conversation",
                    search_result="",
                    reader_result="",
                    writer_result=response,
                    critic_result="",
                    conversation=st.session_state.pdf_conversation,
                    pdf_name=st.session_state.current_pdf_name,
                    chat_type="pdf"
                )

        st.session_state.active_page = "📘 PDF Chat"
        st.rerun()

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

# ─────────────────────────────────────────────────────────────
# PIPELINE FUNCTION
# ─────────────────────────────────────────────────────────────

def render_pipeline(active_step=None, completed_steps=[]):

    if (
        "pipeline_placeholder" not in globals()
        and "pipeline_placeholder" not in locals()
    ):
        return

    steps = [
        ("search", "🔍 Search Agent"),
        ("reader", "📄 Reader Agent"),
        ("writer", "✍️ Writer Chain"),
        ("critic", "🧐 Critic Chain")
    ]

    html = ""

    for key, label in steps:

        if key == active_step:

            status = "🟡 RUNNING"
            css = "running"

        elif key in completed_steps:

            status = "🟢 COMPLETED"
            css = "done"

        else:

            status = "⚪ WAITING"
            css = "waiting"

        html += f"""
        <div class="pipeline-card {css}">
            {label}
            <div style="float:right;">
                {status}
            </div>
        </div>
        """

    pipeline_placeholder.markdown(
        html,
        unsafe_allow_html=True
    )


# INITIAL PIPELINE RENDER

if selected_page == "🔬 AI Research":
    render_pipeline()


# ─────────────────────────────────────────────────────────────
# RUN RESEARCH PIPELINE
# ─────────────────────────────────────────────────────────────

if (
    selected_page == "🔬 AI Research"
    and run_btn
):

    if not topic.strip():

        st.warning("Please enter a research topic.")

    else:

        st.session_state.results = {}

        chat_title = generate_chat_title(
            topic,
            os.getenv("MISTRAL_API_KEY")
        )
        # SEARCH + READER AGENTS (PARALLEL)

        render_pipeline(
            active_step="search",
            completed_steps=[]
        )

        search_agent = build_search_agent()
        reader_agent = build_reader_agent()

        with ThreadPoolExecutor() as executor:

            future_search = executor.submit(
                search_agent.invoke,
                {
                    "input": f"Find recent detailed information about {topic}"
                }
            )

            future_reader = executor.submit(
                reader_agent.invoke,
                {
                    "input": f"""
                    Analyze recent trends, insights,
                    developments and statistics about:

                    {topic}
                    """
                }
            )

            search_response = future_search.result()

            render_pipeline(
                active_step="reader",
                completed_steps=["search"]
            )

            reader_response = future_reader.result()

        search_result = str(search_response)

        reader_result = str(reader_response)

        st.session_state.results["search"] = search_result

        st.session_state.results["reader"] = reader_result

        render_pipeline(
            active_step=None,
            completed_steps=["search", "reader"]
        )


        # WRITER CHAIN

        render_pipeline(
            active_step="writer",
            completed_steps=["search", "reader"]
        )

        combined_research = f"""
        SEARCH RESULTS:
        {search_result}

        SCRAPED CONTENT:
        {reader_result}
        """

        writer_result = writer_chain.invoke({
            "topic": topic,
            "research": combined_research
        })

        st.session_state.results["writer"] = writer_result


        render_pipeline(
            active_step=None,
            completed_steps=["search", "reader", "writer"]
        )

        # CRITIC CHAIN

        render_pipeline(
            active_step="critic",
            completed_steps=["search", "reader", "writer"]
        )

        critic_result = critic_chain.invoke({
            "report": writer_result
        })

        st.session_state.results["critic"] = critic_result

        render_pipeline(
            active_step=None,
            completed_steps=["search", "reader", "writer", "critic"]
        )

        st.success("✅ Research Pipeline Completed!")
        st.session_state.voice_text = ""

        if not st.session_state.is_guest:

            if st.session_state.current_chat_id is None:

                save_chat(
                    user_email=get_user_email(),
                    title=chat_title,
                    topic=topic,
                    search_result=search_result,
                    reader_result=reader_result,
                    writer_result=writer_result,
                    critic_result=critic_result,
                    conversation=st.session_state.conversation,
                    chat_type="web"
                )

                latest_chat = get_all_chats(
                    get_user_email()
                )[0]

                st.session_state.current_chat_id = latest_chat[0]

            else:

                update_chat(
                    chat_id=st.session_state.current_chat_id,
                    topic=topic,
                    search_result=search_result,
                    reader_result=reader_result,
                    writer_result=writer_result,
                    critic_result=critic_result,
                    conversation=st.session_state.conversation,
                    chat_type="web"
                )

# ─────────────────────────────────────────────────────────────
# RESULTS
# ─────────────────────────────────────────────────────────────

results = st.session_state.results

if results:

    st.markdown("---")

    st.markdown("## 📝 Final Results")

    if "search" in results:

        with st.expander("🔍 Search Results"):

            st.write(results["search"])

    if "reader" in results:

        with st.expander("📄 Reader Output"):

            st.write(results["reader"])

    if "writer" in results:

        st.markdown("### 📝 Final Research Report")

        st.markdown(results["writer"])

        st.download_button(
            label="⬇ Download Report",
            data=results["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown"
        )

    if "critic" in results:

        st.markdown("### 🧐 Critic Feedback")

        st.markdown(results["critic"])


# ─────────────────────────────────────────────────────────────
# CONTINUATION CHAT
# ─────────────────────────────────────────────────────────────

if results:

    st.markdown("---")

    st.markdown("## 💬 Continue Conversation")

    st.markdown(
        '<div class="chat-container">',
        unsafe_allow_html=True
    )

    # DISPLAY CHAT HISTORY

    for msg in st.session_state.conversation:

        if msg["role"] == "user":

            st.markdown(
                f'''
                <div class="user-msg">
                    {msg["content"]}
                </div>
                ''',
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                f'''
                <div class="ai-msg">
                    {msg["content"]}
                </div>
                ''',
                unsafe_allow_html=True
            )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

    # FOLLOW-UP INPUT

    st.markdown("### 🎤 Voice Follow-up")

    follow_audio = mic_recorder(
        start_prompt="🎙️ Start Recording Follow-up",
        stop_prompt="🛑 Stop Recording",
        key="followup_recorder",
        just_once=True,
        use_container_width=True
    )

    # SESSION STATES

    if "followup_text" not in st.session_state:

        st.session_state.followup_text = ""

    if "followup_counter" not in st.session_state:

        st.session_state.followup_counter = 0

    # TRANSCRIBE AUDIO

    if follow_audio:

        with st.spinner("Transcribing follow-up..."):

            follow_transcript = transcribe_audio(
                follow_audio["bytes"]
            )

            st.session_state.followup_text = (
                follow_transcript
            )

    # TEXT AREA

    followup = st.text_area(
        "Follow-up Question",
        value=st.session_state.followup_text,
        placeholder="Speak or type follow-up...",
        height=100,
        key=f"followup_{st.session_state.followup_counter}"
    )

    # SEND BUTTON

    send_followup = st.button(
        "🚀 Send Follow-up",
        use_container_width=True
    )

    # HANDLE FOLLOW-UP

    if send_followup and followup.strip():

        st.session_state.conversation.append({
            "role": "user",
            "content": followup
        })

        # BUILD CONTEXT

        full_context = ""

        recent_messages = st.session_state.conversation[-6:]

        for msg in recent_messages:

            role = msg["role"]
            content = msg["content"]

            full_context += f"{role}: {content}\n\n"

        # FAST MODEL

        llm = ChatMistralAI(
            model="ministral-3b-latest",
            temperature=0.4,
            mistral_api_key=os.getenv("MISTRAL_API_KEY")
        )

        # GENERATE RESPONSE

        response = llm.invoke(f"""
        Continue the conversation naturally.

        Previous Conversation:
        {full_context}

        User:
        {followup}
        """)

        ai_reply = response.content

        st.session_state.conversation.append({
            "role": "assistant",
            "content": ai_reply
        })

        # UPDATE DATABASE

        if not st.session_state.is_guest:

            update_chat(
                chat_id=st.session_state.current_chat_id,
                topic=st.session_state.selected_topic,
                search_result=st.session_state.results.get("search", ""),
                reader_result=st.session_state.results.get("reader", ""),
                writer_result=st.session_state.results.get("writer", ""),
                critic_result=st.session_state.results.get("critic", ""),
                conversation=st.session_state.conversation
            )

        # REFRESH UI
        st.session_state.followup_text = ""
        st.session_state.followup_counter += 1
        st.session_state.active_page = "🔬 AI Research"
        st.rerun()