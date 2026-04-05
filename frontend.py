"""
SlideDeck AI Creator - Streamlit UI
"""
import time
import httpx
import streamlit as st

URL_BACKEND = "http://127.0.0.1:8000"
REQ_TIMEOUT = 300

st.set_page_config(page_title="AI Slide Creator", page_icon="📝", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif !important;
}

/* Background & general text - Soft airy blueish white */
.stApp {
    background: radial-gradient(circle at top left, #ebf8ff 0%, #f4f7fb 100%);
    color: #334155;
}

/* Typography - Vibrant Professional Gradient */
.hero-title {
    text-align: center; 
    background: linear-gradient(120deg, #1d4ed8, #0ea5e9, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800; 
    font-size: 3.5rem;
    margin-bottom: 0.25rem;
    letter-spacing: -0.02em;
}
.sub-title { 
    text-align: center; 
    color: #475569; 
    font-size: 1.15rem;
    margin-bottom: 3rem; 
    font-weight: 400;
}

/* Cards (Slides preview) */
.card { 
    background: #ffffff; 
    border-left: 4px solid #3b82f6;
    border-top: 1px solid #e2e8f0;
    border-right: 1px solid #e2e8f0;
    border-bottom: 1px solid #e2e8f0;
    border-radius: 12px; 
    padding: 24px 32px; 
    margin-bottom: 20px;
    box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.05), 0 2px 4px -1px rgba(59, 130, 246, 0.03);
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-left-color 0.2s ease;
}
.card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.1), 0 4px 6px -2px rgba(59, 130, 246, 0.05);
    border-left-color: #8b5cf6;
}
.slide-num { 
    font-size: 0.8rem; 
    color: #8b5cf6; 
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 10px;
}
.slide-heading { 
    font-size: 1.6rem; 
    color: #1e3a8a; 
    margin-top: 0; 
    margin-bottom: 16px; 
    font-weight: 700;
}
.point { 
    font-size: 1.05rem; 
    color: #334155; 
    margin-left: 20px; 
    margin-bottom: 12px;
    text-indent: -18px; 
    line-height: 1.6;
}
.point::before { 
    content: "✨ "; 
    font-size: 1rem;
}

/* Forms & Inputs */
div[data-testid="stForm"] {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(14, 165, 233, 0.2);
    border-radius: 16px;
    padding: 2.5rem;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
}

textarea:focus, input:focus {
    border-color: #0ea5e9 !important;
    box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.2) !important;
}

/* Primary Button */
button[kind="secondaryFormSubmit"] {
    background: linear-gradient(135deg, #2563eb, #6366f1) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.7rem 2.5rem !important;
    font-weight: 600 !important;
    font-size: 1.05rem !important;
    letter-spacing: 0.02em !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.3) !important;
}
button[kind="secondaryFormSubmit"]:hover {
    background: linear-gradient(135deg, #1d4ed8, #4f46e5) !important;
    box-shadow: 0 8px 12px -2px rgba(37, 99, 235, 0.4) !important;
    transform: translateY(-2px) !important;
}
</style>
""", unsafe_allow_html=True)

def is_online():
    try:
        return httpx.get(f"{URL_BACKEND}/api/v1/ping", timeout=3).status_code == 200
    except:
        return False

def call_build(query: str, total: int):
    res = httpx.post(f"{URL_BACKEND}/api/v1/build", json={"query": query, "total_slides": total}, timeout=REQ_TIMEOUT)
    res.raise_for_status()
    return res.json()

def call_export():
    res = httpx.get(f"{URL_BACKEND}/api/v1/export", timeout=60)
    res.raise_for_status()
    return res.content

def call_reload(struct: dict):
    res = httpx.post(f"{URL_BACKEND}/api/v1/reload", json={"structure": struct}, timeout=REQ_TIMEOUT)
    res.raise_for_status()
    return res.json()

if "deck" not in st.session_state:
    st.session_state.update({
        "deck": None,
        "is_ready": False,
        "pptx_data": None,
        "query_text": "",
        "slide_count": 5,
        "err_msg": None
    })

st.markdown('<div class="hero-title">AI Slide Creator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Generate presentations in seconds</div>', unsafe_allow_html=True)

if not is_online():
    st.error("Backend Server is unreachable. Please run: uvicorn server:app --reload")

with st.form("builder_form"):
    q = st.text_area("What should the presentation be about?", value=st.session_state.query_text, height=100)
    c = st.number_input("Number of Slides", min_value=3, max_value=10, value=st.session_state.slide_count)
    submit = st.form_submit_button("Generate Presentation")

if submit and q:
    st.session_state.query_text = q
    st.session_state.slide_count = c
    
    with st.spinner("Building your presentation... This may take a minute."):
        try:
            out = call_build(q, c)
            st.session_state.deck = out.get("structure")
            time.sleep(1)
            st.session_state.pptx_data = call_export()
            st.session_state.is_ready = True
            st.session_state.err_msg = None
        except Exception as e:
            st.session_state.err_msg = str(e)

if st.session_state.err_msg:
    st.error(st.session_state.err_msg)

if st.session_state.is_ready and st.session_state.deck:
    deck = st.session_state.deck
    slides = deck.get("slide_content", [])
    
    st.success(f"Success! Generated '{deck.get('deck_title')}' with {len(slides)} slides.")
    
    st.download_button("Download PPTX", data=st.session_state.pptx_data, file_name="SlideDeck.pptx", mime="application/vnd.openxmlformats-officedocument.presentationml.presentation")
    
    st.markdown("### Slide Preview")
    for i, s in enumerate(slides, 1):
        points_html = "".join([f'<div class="point">{p}</div>' for p in s.get("items", [])])
        st.markdown(f'''
        <div class="card">
            <div class="slide-num">SLIDE {i}</div>
            <div class="slide-heading">{s.get("heading", "")}</div>
            {points_html}
        </div>
        ''', unsafe_allow_html=True)