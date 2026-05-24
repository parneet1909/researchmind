import streamlit as st


def initialize_session_state():

    defaults = {

        "results": {},
        "selected_topic": "",
        "research_topic": "",

        "current_chat_id": None,

        "conversation": [],
        "pdf_conversation": [],

        "user": None,
        "is_guest": False,

        "voice_text": "",
        "followup_text": "",

        "active_page": "🔬 AI Research",

        "followup_counter": 0,

        "current_pdf_name": None
    }

    for key, value in defaults.items():

        if key not in st.session_state:

            st.session_state[key] = value