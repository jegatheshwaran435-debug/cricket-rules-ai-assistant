import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import streamlit as st
from dotenv import load_dotenv

# Ensure root directory is on Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Ensure UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.rag_engine import (
    query_cricket_rules,
    GUARDRAIL_FALLBACK_MESSAGE,
    VECTOR_DIR,
    COLLECTION_NAME,
    VISUAL_COLLECTION_NAME
)
from src.ingest import build_vector_store
from src.generate_visuals import generate_all_visuals

# Standalone definition of dynamic rule links directly in app.py
def get_dynamic_rule_link(law_identifier: str = "", *args, **kwargs) -> str:
    law_str = str(law_identifier).lower()
    if args:
        law_str += " " + " ".join(str(a).lower() for a in args)
    if "36" in law_str or "lbw" in law_str:
        return "https://www.lords.org/mcc/the-laws-of-cricket/leg-before-wicket"
    elif "33" in law_str or "caught" in law_str or "catch" in law_str:
        return "https://www.lords.org/mcc/the-laws-of-cricket/caught"
    elif "20" in law_str or "dead" in law_str:
        return "https://www.lords.org/mcc/the-laws-of-cricket/dead-ball"
    elif "21" in law_str or "no ball" in law_str:
        return "https://www.lords.org/mcc/the-laws-of-cricket/no-ball"
    elif "28" in law_str or "helmet" in law_str or "equipment" in law_str:
        return "https://www.lords.org/mcc/the-laws-of-cricket/fielders-equipment"
    elif "31" in law_str or "appeal" in law_str:
        return "https://www.lords.org/mcc/the-laws-of-cricket/appeals"
    elif "38" in law_str or "run out" in law_str or "mankad" in law_str:
        return "https://www.lords.org/mcc/the-laws-of-cricket/run-out"
    elif "40" in law_str or "timed out" in law_str or "mathews" in law_str:
        return "https://www.lords.org/mcc/the-laws-of-cricket/timed-out"
    elif "34" in law_str or "twice" in law_str:
        return "https://www.lords.org/mcc/the-laws-of-cricket/hit-the-ball-twice"
    elif "22" in law_str or "wide" in law_str:
        return "https://www.lords.org/mcc/the-laws-of-cricket/wide-ball"
    elif "19" in law_str or "boundary" in law_str or "boundaries" in law_str:
        return "https://www.lords.org/mcc/the-laws-of-cricket/boundaries"
    return "https://www.lords.org/mcc/the-laws-of-cricket"

# Load environment variables
load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="Cricket Rules AI Assistant",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Production-grade CSS styling
st.markdown("""
<style>
    /* Main Layout Aesthetics */
    .stApp {
        background-color: #0c1417;
        color: #f1f5f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Header Banners */
    .hero-container {
        background: linear-gradient(135deg, #064e3b 0%, #0f172a 100%);
        border: 1px solid #059669;
        border-radius: 12px;
        padding: 24px 30px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: #ffffff;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .hero-subtitle {
        font-size: 1.0rem;
        color: #a7f3d0;
        margin-top: 8px;
        line-height: 1.5;
    }
    
    /* Visual Explainer Cards */
    .visual-card-frame {
        background-color: #111e24;
        border: 2px solid #059669;
        border-radius: 12px;
        padding: 16px;
        margin: 16px 0;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
    }
    .visual-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px solid #1e3a47;
    }
    .visual-badge {
        background: #065f46;
        color: #34d399;
        font-weight: 700;
        font-size: 0.85rem;
        padding: 4px 10px;
        border-radius: 6px;
        border: 1px solid #10b981;
    }
    .visual-law-tag {
        color: #f59e0b;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .visual-caption {
        font-size: 0.9rem;
        color: #94a3b8;
        font-style: italic;
        text-align: center;
        margin-top: 8px;
    }

    /* Guardrail Warning Box */
    .guardrail-alert {
        background-color: #451a03;
        border-left: 5px solid #f59e0b;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin-top: 10px;
        color: #fef3c7;
        font-size: 0.95rem;
    }

    /* Sidebar Tweaks */
    section[data-testid="stSidebar"] {
        background-color: #080f12;
        border-right: 1px solid #1e293b;
    }
</style>
""", unsafe_allow_html=True)


def check_kb_status():
    """Check knowledge base collections and counts."""
    if not VECTOR_DIR.exists():
        return False, 0, 0
    try:
        import chromadb
        client = chromadb.PersistentClient(path=str(VECTOR_DIR))
        collections = client.list_collections()
        law_cnt, vis_cnt = 0, 0
        has_laws = False
        for col in collections:
            if col.name == COLLECTION_NAME:
                has_laws = True
                law_cnt = col.count()
            elif col.name == VISUAL_COLLECTION_NAME:
                vis_cnt = col.count()
        return has_laws, law_cnt, vis_cnt
    except Exception:
        pass
    return False, 0, 0


# ==============================================================================
# SIDEBAR CONFIGURATION & CONTROLS
# ==============================================================================
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/en/thumb/e/eb/International_Cricket_Council_logo.svg/320px-International_Cricket_Council_logo.svg.png",
        width=110
    )
    st.header("⚙️ Configuration")

    # API Key Input
    env_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
    api_key_input = st.text_input(
        "Google Gemini API Key",
        value=env_key,
        type="password",
        help="Enter your Google Gemini API Key. Can also be set as GEMINI_API_KEY in .env"
    )

    # Reference Link Buttons
    st.link_button(
        "🔑 Get Gemini API Key",
        "https://aistudio.google.com/app/apikey",
        use_container_width=True
    )
    st.link_button(
        "📜 Official ICC & MCC Rules",
        "https://www.icc-cricket.com/about/cricket/rules-and-regulations/playing-conditions",
        use_container_width=True
    )
    st.markdown("---")

    # Model selector
    model_choice = st.selectbox(
        "Select LLM Model",
        options=["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"],
        index=0
    )

    # Retrieval Top-K Slider (k=2 primary rule snippets)
    top_k = st.slider("Top-K Rule Snippets", min_value=1, max_value=4, value=2, step=1)

    st.markdown("---")
    st.subheader("📚 Knowledge Base")
    has_kb, law_cnt, vis_cnt = check_kb_status()
    if has_kb and law_cnt > 0:
        st.success(f"Indexed: **{law_cnt}** Rules • **{vis_cnt}** Visuals")
    else:
        st.warning("Knowledge Base not indexed yet.")

    if st.button("🔄 Re-Index Knowledge & Visuals", use_container_width=True):
        with st.spinner("Generating visuals & indexing database..."):
            try:
                generate_all_visuals()
                laws_total, vis_total = build_vector_store()
                st.success(f"Indexed {laws_total} rule chunks & {vis_total} visual explainers!")
                st.rerun()
            except Exception as e:
                st.error(f"Error during re-indexing: {e}")

    st.markdown("---")
    st.subheader("💡 Visual Scenario Questions")
    sample_questions = [
        "What are the rules for an LBW dismissal?",
        "What happens if the ball hits the helmet resting on the ground behind the keeper?",
        "What are the rules for a front-foot No Ball?",
        "What is a waist-high full toss beamer?",
        "What are the rules for Timed Out (e.g. Angelo Mathews dismissal)?",
        "Can a batter hit the ball twice to defend their stumps?",
        "What are the rules and tramlines for calling a Wide Ball?",
        "What are the rules for an airborne relay catch on the boundary?",
        "How do Powerplay and 30-yard circle fielding restrictions work?",
        "Can a bowler run out a non-striker backing up early (Mankad)?",
        "What is Umpire's Call in a DRS LBW review?",
        "How is a tied Super Over decided?",
        "What is the difference between Stumped and Run Out?",
        "When is a batter out for obstructing the field?",
        "What is the offside rule in football? (Guardrail Test)"
    ]

    selected_sample = None
    for q in sample_questions:
        if st.button(q, key=f"btn_{q}", use_container_width=True):
            selected_sample = q


# ==============================================================================
# MAIN CHAT WINDOW
# ==============================================================================

# Hero Header Banner
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🏏 Cricket Rules AI Assistant <span style="font-size: 1.1rem; color: #34d399; font-weight: 500;">(Visual RAG Edition)</span></div>
    <div class="hero-subtitle">
        Grounding official <b>MCC Laws of Cricket</b> & <b>ICC Playing Conditions</b> with high-resolution 16:9 visual scenario explainers, exact clause citations, and hallucination guardrails.
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Welcome! I am your **Cricket Rules AI Assistant**. Ask me any complex scenario regarding official cricket laws (e.g. LBW Hawkeye projection, Ball hitting resting helmet, Mankad, Waist-high beamer, Boundary relay catches, DRS Umpire's Call) and I will provide an authoritative rule citation alongside a high-definition visual explainer.",
            "sources": [],
            "visual_scenario": None
        }
    ]


def render_visual_block(visual: Dict[str, Any]):
    """Renders a centered high-definition 16:9 visual explainer card."""
    if not visual:
        return
        
    img_path = visual.get("full_path") or visual.get("file_path")
    if not img_path or not Path(img_path).exists():
        # Try relative to ROOT_DIR
        candidate = ROOT_DIR / visual.get("file_path", "")
        if candidate.exists():
            img_path = str(candidate)
        else:
            return

    # Step 2: Visual section heading
    st.markdown("### 🖼️ Visual Scenario Explainer")

    st.markdown(f"""
    <div class="visual-card-frame">
        <div class="visual-header">
            <span class="visual-badge">📸 {visual.get('title', 'Cricket Scenario')}</span>
            <span class="visual-law-tag">{visual.get('law_reference', 'Official Law')}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Step 3: Display matching retrieved diagram/image centered on screen
    st.image(img_path, caption=f"{visual.get('title', '')} — {visual.get('law_reference', '')}", use_container_width=True)
    st.markdown(f'<div class="visual-caption">{visual.get("description", "")}</div>', unsafe_allow_html=True)


# Render Past Chat Messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # Render visual explainer if message has one
        if msg.get("visual_scenario"):
            render_visual_block(msg["visual_scenario"])

        # Render Source Inspector Accordion below the image
        if msg.get("sources"):
            with st.expander(f"🔍 View Retrieved Law Snippets ({len(msg['sources'])} Law Snippets)"):
                for i, src in enumerate(msg["sources"], 1):
                    law_num = src.get("law_number", "Official Law")
                    sec_title = src.get("section_title", "Cricket Law")
                    dist = src.get("distance", 0.0)
                    rule_url = get_dynamic_rule_link(law_num, sec_title)
                    st.markdown(f"**Snippet {i}:** `{law_num}` — *{sec_title}* `(similarity dist: {dist:.3f})`")
                    st.markdown(f"- 📌 **Read Official {law_num} Clause:** [{rule_url}]({rule_url})")
                    st.text(src.get("text", "").strip())
                    st.markdown("---")
                if msg.get("visual_scenario"):
                    vis = msg["visual_scenario"]
                    st.markdown(f"**Visual Scenario Matched:** `{vis.get('title')}` `(similarity dist: {vis.get('distance', 0.0):.3f})`")
                    st.caption(f"Asset File: `{vis.get('file_path')}` • Law Ref: `{vis.get('law_reference')}`")


# User Input Handling
user_prompt = st.chat_input("Ask any question on cricket rules or visual scenarios...")
if selected_sample:
    user_prompt = selected_sample

if user_prompt:
    # 1. Append and render user prompt
    st.session_state.messages.append({
        "role": "user",
        "content": user_prompt,
        "sources": [],
        "visual_scenario": None
    })
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # 2. Assistant Response Synthesis
    with st.chat_message("assistant"):
        with st.spinner("Consulting MCC Laws & Visual Scenario Database..."):
            result = query_cricket_rules(
                query=user_prompt,
                k=top_k,
                api_key=api_key_input,
                model_name=model_choice
            )
            answer_text = result["answer"]
            sources = result.get("sources", [])
            visual_scenario = result.get("visual_scenario")
            guardrail_hit = result.get("guardrail_triggered", False)

            # Step 1: Detailed textual rule explanation
            st.markdown(answer_text)

            # Step 2 & 3: Render visual section heading and centered visual diagram
            if visual_scenario and not guardrail_hit:
                render_visual_block(visual_scenario)

            # If guardrail triggered, display informative badge
            if guardrail_hit:
                st.markdown(
                    '<div class="guardrail-alert">🛡️ <b>Guardrail Enforced:</b> Query is outside the scope of MCC Laws of Cricket or ICC Playing Conditions. No visual scenario displayed.</div>',
                    unsafe_allow_html=True
                )

            # Step 4: Include the expandable "🔍 View Retrieved Law Snippets" source inspector accordion at bottom
            if sources and not guardrail_hit:
                with st.expander(f"🔍 View Retrieved Law Snippets ({len(sources)} Law Snippets)"):
                    for i, src in enumerate(sources, 1):
                        law_num = src.get("law_number", "Official Law")
                        sec_title = src.get("section_title", "Cricket Law")
                        dist = src.get("distance", 0.0)
                        rule_url = get_dynamic_rule_link(law_num, sec_title, user_prompt)
                        st.markdown(f"**Snippet {i}:** `{law_num}` — *{sec_title}* `(similarity dist: {dist:.3f})`")
                        st.markdown(f"- 📌 **Read Official {law_num} Clause:** [{rule_url}]({rule_url})")
                        st.text(src.get("text", "").strip())
                        st.markdown("---")
                    if visual_scenario:
                        st.markdown(f"**Visual Scenario Matched:** `{visual_scenario.get('title')}` `(similarity dist: {visual_scenario.get('distance', 0.0):.3f})`")
                        st.caption(f"Asset File: `{visual_scenario.get('file_path')}` • Law Ref: `{visual_scenario.get('law_reference')}`")

            # Store in session state
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer_text,
                "sources": sources,
                "visual_scenario": visual_scenario
            })

# Clear Chat Option at the bottom
if len(st.session_state.messages) > 1:
    col1, col2 = st.columns([1, 6])
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = [st.session_state.messages[0]]
            st.rerun()
