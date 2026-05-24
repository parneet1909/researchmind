import streamlit as st


def load_css():

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
                
    /* HERO */

.hero {
    text-align: center;
    padding-top: 0.5rem;
    padding-bottom: 2rem;
}

.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: 5rem;
    font-weight: 800;
    color: #f5efe6;
    margin-bottom: 1rem;
    line-height: 1;
    letter-spacing: -2px;
}

.hero h1 span {
    color: #ff8c32;
}

.hero-sub {

    width: 100%;
    max-width: 860px;

    margin: auto;

    padding: 12px 20px;

    background: rgba(255,255,255,0.045);

    border: 1px solid rgba(255,255,255,0.04);

    border-radius: 6px;

    color: #f0ebe0;

    font-size: 0.92rem;

    line-height: 1.6;

    text-align: center;

    box-shadow:
        0 0 20px rgba(0,0,0,0.25);

    backdrop-filter: blur(10px);
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
    /* HIDE DEFAULT STREAMLIT PAGES SIDEBAR */

    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    </style>
    """, unsafe_allow_html=True)