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
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;900&display=swap');
html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif !important;
}
.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
    color: #e2e8f0;
}
.hero-title {
    text-align: center; 
    background: linear-gradient(to right, #38bdf8, #818cf8, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 900; 
    font-size: 3.5rem;
    margin-bottom: 0.5rem;
    animation: fadeInDown 0.8s ease-out;
}
.sub-title { 
    text-align: center; 
    color: #94a3b8; 
    font-size: 1.2rem;
    margin-bottom: 2.5rem; 
    font-weight: 300;
}
.card { 
    background: rgba(255, 255, 255, 0.05); 
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px; 
    padding: 24px; 
    margin-bottom: 20px;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    border: 1px solid rgba(139, 92, 246, 0.3);
}
.slide-num { 
    font-size: 0.75rem; 
    color: #a78bfa; 
    letter-spacing: 2px;
    text-transform: uppercase;
    font-weight: 600;
    margin-bottom: 8px;
}
.slide-heading { 
    font-size: 1.6rem; 
    color: #f8fafc; 
    margin-top: 0; 
    margin-bottom: 15px; 
    font-weight: 600;
}
.point { 
    font-size: 1.05rem; 
    color: #cbd5e1; 
    margin-left: 20px; 
    margin-bottom: 8px;
    text-indent: -20px; 
    line-height: 1.5;
}
.point::before { 
    content: "✦ "; 
    color: #38bdf8; 
    font-size: 1.2rem;
}
/* Form Styling Customizations */
div[data-testid="stForm"] {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 2rem;
}
button[kind="secondaryFormSubmit"] {
    background: linear-gradient(90deg, #6366f1, #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.5rem 2rem !important;
    font-weight: 600 !important;
    transition: opacity 0.2s !important;
}
button[kind="secondaryFormSubmit"]:hover {
    opacity: 0.9 !important;
}
@keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
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