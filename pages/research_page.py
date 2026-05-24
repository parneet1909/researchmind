import streamlit as st

from streamlit_mic_recorder import (
    mic_recorder
)

from utils.voice_utils import (
    transcribe_audio
)


def render_research_input():

    left_col, right_col = st.columns([5, 4])

    with left_col:

        st.markdown(
            '<div class="input-card">',
            unsafe_allow_html=True
        )

        st.markdown(
            "## 🔬 Research Assistant"
        )

        st.markdown(
            "### 🎤 Voice Research Input"
        )

        # SESSION STATE

        if "research_topic" not in st.session_state:

            st.session_state.research_topic = (
                st.session_state.selected_topic
            )

        # VOICE RECORDER

        audio = mic_recorder(
            start_prompt="🎙️ Start Recording",
            stop_prompt="🛑 Stop Recording",
            just_once=True,
            use_container_width=True
        )

        # TRANSCRIBE

        if audio:

            with st.spinner(
                "Transcribing voice..."
            ):

                transcript = transcribe_audio(
                    audio["bytes"]
                )

                # UPDATE ONLY IF VALID

                if transcript.strip():

                    st.session_state.voice_text = (
                        transcript
                    )

                    st.session_state.research_topic = (
                        transcript
                    )

        # TEXT AREA

        topic = st.text_area(
            "Research Topic",
            key="research_topic",
            placeholder=(
                "Speak or type your "
                "research topic..."
            ),
            height=120
        )

        # RUN BUTTON

        run_btn = st.button(
            "⚡ Run Research Pipeline",
            use_container_width=True
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    with right_col:

        st.markdown("## 🔬 Pipeline")

        pipeline_placeholder = st.empty()

    return (
        topic,
        run_btn,
        pipeline_placeholder
    )