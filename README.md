# 🏏 Cricket Rules AI Assistant (Visual RAG Edition)

A high-accuracy, lightweight **Retrieval-Augmented Generation (RAG)** application built to ingest official **Marylebone Cricket Club (MCC) Laws of Cricket** and **ICC Playing Conditions**, answering user queries with precise rule citations and dynamic, high-definition **16:9 visual scenario explainers**.

---

## 🌟 Key Features

- **Dual-Stream Visual RAG Pipeline**:
  - Primary retrieval: Top `k=2` official MCC rule snippets from `cricket_laws`.
  - Secondary retrieval: Specialized semantic search against ChromaDB `visual_scenarios` to fetch matching high-resolution visual infographics.
- **Library of 12 High-Definition 16:9 Visual Explainers**:
  1. *Hawkeye LBW Projection* (Pitching spot, Impact in-line red/blue zones, Wicket hitting).
  2. *Ball Striking Resting Helmet* (Law 28.3 - 5 penalty runs, dead ball).
  3. *Dead Ball & Boundary Interception* (Law 19 / Law 20).
  4. *Front-Foot & Back-Foot Crease Faults* (Law 21.5 No-Ball).
  5. *Waist-High Full Toss Beamer* (Law 21.9 No-Ball & Free Hit).
  6. *Powerplay & 30-Yard Circle Fielding Restrictions* (ICC Standard Playing Conditions).
  7. *Mankad Non-Striker Run Out* (Law 38.3 leaving crease early).
  8. *Boundary Airborne Relay Catch* (Law 33.2 fair catch criteria).
  9. *Stumped vs Run Out Distinction* (Law 38 vs Law 39 comparison).
  10. *DRS Ball Tracking & Umpire's Call Zones* (50% ball threshold).
  11. *Super Over Tie-Breaker Procedure* (6 balls, 2 wickets, tie resolution).
  12. *Obstructing the Field* (Law 37 wilful diversion vs accidental contact).
- **Multimodal Grounding**: The AI seamlessly references the retrieved visual explainer in its answer prose (e.g. *"As illustrated in the [Title] diagram below..."*).
- **Hallucination Guardrail**: Unrelated queries trigger an immediate fallback without attaching random images:
  > *"I could not find a specific cricket rule covering this in the official laws."*
- **Production UI Overhaul**:
  - All configuration (API key, model selection, links, re-indexing) tucked into the **Sidebar**.
  - **Main Window** dedicated to a clean, focused conversation stream.
  - Centered high-definition 16:9 visual card followed by a collapsible **"Source Inspector"** accordion.

---

## 📁 Project Structure

```text
KE-proj/
├── data/
│   ├── images/                # 12 High-definition 16:9 visual scenario infographics
│   │   ├── lbw_hawkeye_projection.png
│   │   ├── dead_ball_helmet_ground.png
│   │   ├── powerplay_fielding_restrictions.png
│   │   └── ... (9 more)
│   └── mcc_cricket_laws.txt   # Curated official MCC Laws & ICC Playing Conditions
├── src/
│   ├── __init__.py
│   ├── generate_visuals.py    # Generates the 12 visual scenario infographics
│   ├── ingest.py              # Ingests both text laws and visual scenarios into ChromaDB
│   ├── rag_engine.py          # Dual retrieval (k=2 text + visual) & multimodal grounding
│   └── app.py                 # Streamlit chat UI with centered visual cards
├── tests/
│   └── test_rag.py            # Comprehensive verification test suite
├── vectorstore/               # Local ChromaDB persistent collections
├── requirements.txt           # Project dependencies
└── README.md                  # Documentation and execution guide
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ (Python 3.11 recommended)
- Optional: Google Gemini API Key ([Get one free from Google AI Studio](https://aistudio.google.com/app/apikey))

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Generate Visuals & Ingest Database
```bash
# Generate the 12 visual infographics
python src/generate_visuals.py

# Ingest text laws & visual scenarios into ChromaDB
python src/ingest.py
```

### 4. Launch the Streamlit Web Application
```bash
streamlit run src/app.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser.

---

## 🧪 Verification & Test Suite

Run the automated verification suite covering text retrieval, visual matching, guardrail enforcement, and official links:
```bash
python tests/test_rag.py
```
Expected output:
```text
Running Cricket Rules Visual RAG verification suite...

[Test 1] Helmet on ground (Law 28.3) and visual explainer successfully verified.
[Test 2] LBW rule (Law 36) and Hawkeye visual explainer successfully verified.
[Test 3] Guardrail successfully triggered and suppressed visual attachments.
[Test 4] Official API key and rule links returned accurately.
[Test 5] Additional specialized visual scenarios verified (Mankad, Powerplay).

[SUCCESS] ALL VISUAL RAG VERIFICATION TESTS PASSED SUCCESSFULLY!
```
