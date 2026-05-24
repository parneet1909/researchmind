import os
import streamlit as st

from streamlit_mic_recorder import (
    mic_recorder
)

from utils.voice_utils import transcribe_audio

from langchain_mistralai import (
    ChatMistralAI
)

from database.memory_db import update_chat


def render_followup_chat():

    results = st.session_state.results

    if not results:

        return

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

    # TRANSCRIBE

    if follow_audio:

        with st.spinner(
            "Transcribing follow-up..."
        ):

            follow_transcript = (
                transcribe_audio(
                    follow_audio["bytes"]
                )
            )

            st.session_state.followup_text = (
                follow_transcript
            )

    # TEXT AREA

    followup = st.text_area(
        "Follow-up Question",
        value=(
            st.session_state.followup_text
        ),
        placeholder=(
            "Speak or type follow-up..."
        ),
        height=100,
        key=(
            f"followup_"
            f"{st.session_state.followup_counter}"
        )
    )

    # BUTTON

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

        # CONTEXT

        full_context = ""

        recent_messages = (
            st.session_state.conversation[-7:-1]
        )

        for msg in recent_messages:

            role = msg["role"]
            content = msg["content"]

            full_context += (
                f"{role}: {content}\n\n"
            )

        # MODEL

        llm = ChatMistralAI(
            model="ministral-3b-latest",
            temperature=0.4,
            mistral_api_key=os.getenv(
                "MISTRAL_API_KEY"
            )
        )

        # RESPONSE

        with st.spinner("Thinking..."):

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

        # UPDATE DB

        if (
            not st.session_state.is_guest
            and st.session_state.current_chat_id
        ):

            update_chat(
                chat_id=(
                    st.session_state
                    .current_chat_id
                ),
                topic=(
                    st.session_state
                    .selected_topic
                ),
                search_result=(
                    st.session_state.results
                    .get("search", "")
                ),
                reader_result=(
                    st.session_state.results
                    .get("reader", "")
                ),
                writer_result=(
                    st.session_state.results
                    .get("writer", "")
                ),
                critic_result=(
                    st.session_state.results
                    .get("critic", "")
                ),
                conversation=(
                    st.session_state
                    .conversation
                )
            )

        # RESET

        st.session_state.followup_text = ""
        st.session_state.followup_audio = None
        st.session_state.followup_counter += 1

        st.session_state.active_page = (
            "🔬 AI Research"
        )

        st.rerun()