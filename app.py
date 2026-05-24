import streamlit as st
import os

from dotenv import load_dotenv

from database.memory_db import (
    init_db,
    save_chat,
    update_chat,
    get_all_chats
)

from components.sidebar import render_sidebar
from components.results import render_results
from components.followup_chat import render_followup_chat
from components.pipeline import render_pipeline
from components.hero import render_hero

from pages.pdf_page import render_pdf_page
from pages.research_page import (
    render_research_input
)
from pages.auth_page import render_auth_page

from services.research_service import (
    run_research_pipeline
)

from utils.styles import load_css

from utils.session_state import (
    initialize_session_state
)

from utils.title_generator import (
    generate_chat_title
)

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
# ENV SETUP
# ─────────────────────────────────────────────────────────────

load_dotenv()

init_db()

if not os.getenv("MISTRAL_API_KEY"):

    st.error(
        "❌ MISTRAL_API_KEY not found in .env file"
    )

    st.stop()

# ─────────────────────────────────────────────────────────────
# LOAD CSS
# ─────────────────────────────────────────────────────────────

load_css()

initialize_session_state()


# ─────────────────────────────────────────────────────────────
# USER EMAIL
# ─────────────────────────────────────────────────────────────

def get_user_email():

    if st.session_state.user is None:

        return ""

    if st.session_state.is_guest:

        return (
            st.session_state.user["email"]
        )

    return st.session_state.user.email

# ─────────────────────────────────────────────────────────────
# AUTHENTICATION
# ─────────────────────────────────────────────────────────────

if st.session_state.user is None:

    render_auth_page()

    st.stop()

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────

if st.session_state.user is not None:

    with st.sidebar:

        render_sidebar(get_user_email)

# ─────────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────────

render_hero()

# ─────────────────────────────────────────────────────────────
# PAGE NAVIGATION
# ─────────────────────────────────────────────────────────────

selected_page = st.radio(
    "",
    ["🔬 AI Research", "📘 PDF Chat"],
    horizontal=True,
    index=(
        0
        if st.session_state.active_page
        == "🔬 AI Research"
        else 1
    )
)

st.session_state.active_page = (
    selected_page
)

# ─────────────────────────────────────────────────────────────
# AI RESEARCH PAGE
# ─────────────────────────────────────────────────────────────

if selected_page == "🔬 AI Research":

    (
        topic,
        run_btn,
        pipeline_placeholder
    ) = render_research_input()

# ─────────────────────────────────────────────────────────────
# PDF PAGE
# ─────────────────────────────────────────────────────────────

if selected_page == "📘 PDF Chat":

    render_pdf_page(
        get_user_email
    )

# ─────────────────────────────────────────────────────────────
# INITIAL PIPELINE
# ─────────────────────────────────────────────────────────────

if selected_page == "🔬 AI Research":

    render_pipeline(
        pipeline_placeholder
    )

# ─────────────────────────────────────────────────────────────
# RUN PIPELINE
# ─────────────────────────────────────────────────────────────

if (
    selected_page == "🔬 AI Research"
    and run_btn
):

    if not topic.strip():

        st.warning(
            "Please enter a research topic."
        )

    else:

        st.session_state.results = {}

        chat_title = generate_chat_title(
            topic,
            os.getenv(
                "MISTRAL_API_KEY"
            )
        )

        # RUN PIPELINE

        pipeline_results = (
            run_research_pipeline(
                topic,
                lambda **kwargs:
                render_pipeline(
                    pipeline_placeholder,
                    **kwargs
                )
            )
        )

        st.session_state.results = (
            pipeline_results
        )

        st.success(
            "✅ Research Pipeline Completed!"
        )

        st.session_state.voice_text = ""

        # SAVE CHAT

        if not st.session_state.is_guest:

            if (
                st.session_state.current_chat_id
                is None
            ):

                save_chat(
                    user_email=get_user_email(),
                    title=chat_title,
                    topic=topic,
                    search_result=(
                        pipeline_results["search"]
                    ),
                    reader_result=(
                        pipeline_results["reader"]
                    ),
                    writer_result=(
                        pipeline_results["writer"]
                    ),
                    critic_result=(
                        pipeline_results["critic"]
                    ),
                    conversation=(
                        st.session_state
                        .conversation
                    ),
                    chat_type="web"
                )

                latest_chat = (
                    get_all_chats(
                        get_user_email()
                    )[0]
                )

                st.session_state.current_chat_id = (
                    latest_chat[0]
                )

            else:

                update_chat(
                    chat_id=(
                        st.session_state
                        .current_chat_id
                    ),
                    topic=topic,
                    search_result=(
                        pipeline_results["search"]
                    ),
                    reader_result=(
                        pipeline_results["reader"]
                    ),
                    writer_result=(
                        pipeline_results["writer"]
                    ),
                    critic_result=(
                        pipeline_results["critic"]
                    ),
                    conversation=(
                        st.session_state
                        .conversation
                    ),
                    chat_type="web"
                )

# ─────────────────────────────────────────────────────────────
# RESULTS + FOLLOWUP
# ─────────────────────────────────────────────────────────────

results = st.session_state.results

if selected_page == "🔬 AI Research":

    render_results(results)

    render_followup_chat()