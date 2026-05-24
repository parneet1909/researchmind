import streamlit as st

from supabase_client import (
    supabase
)


def render_auth_page():

    # REMOVE HEADER + SIDEBAR COMPLETELY
    st.markdown("""
    <style>

    header {
        display: none !important;
    }

    [data-testid="stToolbar"] {
        display: none !important;
    }

    [data-testid="collapsedControl"] {
        display: none !important;
    }

    button[kind="header"] {
        display: none !important;
    }

    section[data-testid="stSidebar"] {
        display: none !important;
        width: 0px !important;
        min-width: 0px !important;
    }

    .main .block-container {
        max-width: 100% !important;
        padding-top: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    /* AUTH PAGE */

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

    # AUTH CARD START

    st.markdown("""
    <div class="auth-container">

        <div class="auth-card">

            <div class="auth-title">
                Research<span>Mind</span>
            </div>

            <div class="auth-sub">
                Multi-Agent AI platform for deep research,
                intelligent analysis, and PDF conversations.
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