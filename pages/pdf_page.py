import streamlit as st
from services.pdf_service import (
    get_pdf_text,
    get_text_chunks,
    get_vector_store,
    user_input
)

from database.memory_db import (
    save_chat,
    update_chat,
    get_all_chats
)


def render_pdf_page(get_user_email):

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
            st.session_state.current_chat_id = None
            st.session_state.pdf_conversation = []
            st.session_state.results = {}
            st.session_state.conversation = []
            with st.spinner("Processing PDFs..."):
                raw_text = get_pdf_text(pdf_docs)
                text_chunks = get_text_chunks(raw_text)
                get_vector_store(text_chunks)

                # STORE PDF NAME

                pdf_names = [pdf.name for pdf in pdf_docs]
                st.session_state.current_pdf_name = (
                    ", ".join(pdf_names)
                )

                st.success(
                    "✅ PDFs processed successfully!"
                )

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

    # CHAT INPUT

    pdf_question = st.chat_input(
        "Ask anything from your PDF..."
    )

    # HANDLE QUESTION

    if pdf_question:

        st.session_state.pdf_conversation.append({
            "role": "user",
            "content": pdf_question
        })

        with st.spinner("Searching PDF..."):

            try:
                response = user_input(pdf_question)

            except Exception as e:
                response = f"❌ Error: {str(e)}"

        st.session_state.pdf_conversation.append({
            "role": "assistant",
            "content": response
        })


        # SAVE CHAT

        if not st.session_state.is_guest:

            if (
                st.session_state.current_chat_id is None
                or st.session_state.results
            ):

                save_chat(
                    user_email=get_user_email(),
                    title=(
                        st.session_state.current_pdf_name
                        or "PDF Chat"
                    ),
                    topic="PDF Conversation",
                    search_result="",
                    reader_result="",
                    writer_result=response,
                    critic_result="",
                    conversation=(
                        st.session_state
                        .pdf_conversation
                    ),
                    pdf_name=(
                        st.session_state
                        .current_pdf_name
                    ),
                    chat_type="pdf"
                )

                latest_chat = get_all_chats(
                    get_user_email()
                )[0]

                st.session_state.current_chat_id = (
                    latest_chat[0]
                )

            else:

                update_chat(
                    chat_id=(
                        st.session_state
                        .current_chat_id
                    ),
                    topic="PDF Conversation",
                    search_result="",
                    reader_result="",
                    writer_result=response,
                    critic_result="",
                    conversation=(
                        st.session_state
                        .pdf_conversation
                    ),
                    pdf_name=(
                        st.session_state
                        .current_pdf_name
                    ),
                    chat_type="pdf"
                )

        st.session_state.active_page = (
            "📘 PDF Chat"
        )

        st.rerun()

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )