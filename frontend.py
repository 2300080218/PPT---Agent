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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* Background & general text */
.stApp {
    background-color: #f8fafc;
    color: #334155;
}

/* Typography */
.hero-title {
    text-align: center; 
    color: #0f172a;
    font-weight: 800; 
    font-size: 3rem;
    margin-bottom: 0.25rem;
    letter-spacing: -0.025em;
}
.sub-title { 
    text-align: center; 
    color: #64748b; 
    font-size: 1.1rem;
    margin-bottom: 3rem; 
    font-weight: 400;
}

/* Cards (Slides preview) */
.card { 
    background: #ffffff; 
    border: 1px solid #e2e8f0;
    border-radius: 8px; 
    padding: 24px 32px; 
    margin-bottom: 16px;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.03);
    transition: box-shadow 0.2s ease;
}
.card:hover {
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -1px rgba(0, 0, 0, 0.04);
}
.slide-num { 
    font-size: 0.75rem; 
    color: #94a3b8; 
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 12px;
}
.slide-heading { 
    font-size: 1.5rem; 
    color: #0f172a; 
    margin-top: 0; 
    margin-bottom: 16px; 
    font-weight: 700;
    letter-spacing: -0.015em;
}
.point { 
    font-size: 1rem; 
    color: #475569; 
    margin-left: 20px; 
    margin-bottom: 10px;
    text-indent: -18px; 
    line-height: 1.6;
}
.point::before { 
    content: "• "; 
    color: #2563eb; 
    font-size: 1.2rem;
    font-weight: bold;
}

/* Forms & Inputs */
div[data-testid="stForm"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

textarea:focus, input:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2) !important;
}

/* Primary Button */
button[kind="secondaryFormSubmit"] {
    background-color: #0f172a !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.6rem 2.5rem !important;
    font-weight: 500 !important;
    font-size: 1rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
}
button[kind="secondaryFormSubmit"]:hover {
    background-color: #1e293b !important;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15) !important;
    transform: translateY(-1px) !important;
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