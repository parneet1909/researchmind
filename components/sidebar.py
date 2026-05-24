import streamlit as st
import json

from database.memory_db import (
    get_all_chats,
    get_chat,
    delete_chat,
    rename_chat
)

from supabase_client import supabase


def render_sidebar(get_user_email):

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
        st.session_state.followup_text = ""
        st.session_state.followup_counter = 0

        st.rerun()

    # NEW CHAT

    if st.button(
        "➕ New Chat",
        use_container_width=True
    ):

        st.session_state.pdf_conversation = []
        st.session_state.current_pdf_name = None
        st.session_state.results = {}
        st.session_state.selected_topic = ""
        st.session_state.current_chat_id = None
        st.session_state.conversation = []
        st.session_state.voice_text = ""
        st.session_state.followup_text = ""
        st.session_state.followup_counter = 0

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

                    chat_type = (
                        selected_chat[10]
                        if len(selected_chat) > 10
                        else "web"
                    )

                    if chat_type == "web":

                        st.session_state.results = {
                            "search": selected_chat[4],
                            "reader": selected_chat[5],
                            "writer": selected_chat[6],
                            "critic": selected_chat[7]
                        }

                    else:

                        st.session_state.results = {}

                    st.session_state.selected_topic = (
                        selected_chat[3]
                    )

                    saved_conversation = selected_chat[8]

                    try:

                        if (
                            saved_conversation
                            and saved_conversation.strip()
                        ):

                            loaded_conversation = json.loads(
                                saved_conversation
                            )

                            if chat_type == "pdf":

                                st.session_state.pdf_conversation = (
                                    loaded_conversation
                                )

                                st.session_state.conversation = []

                            else:

                                st.session_state.conversation = (
                                    loaded_conversation
                                )

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