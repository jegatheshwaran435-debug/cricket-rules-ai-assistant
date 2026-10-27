import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# Ensure root directory is on Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Ensure UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import chromadb
from dotenv import load_dotenv

# Load local environment
load_dotenv()

VECTOR_DIR = Path(__file__).resolve().parent.parent / "vectorstore"
COLLECTION_NAME = "cricket_laws"
VISUAL_COLLECTION_NAME = "cricket_visual_scenarios"

__all__ = [
    "query_cricket_rules",
    "retrieve_relevant_laws",
    "retrieve_visual_scenario",
    "get_dynamic_rule_link",
    "format_helpful_links_section",
    "MCC_LAW_URL_MAP",
    "GUARDRAIL_FALLBACK_MESSAGE",
    "VECTOR_DIR",
    "COLLECTION_NAME",
    "VISUAL_COLLECTION_NAME",
]

# Official MCC Laws of Cricket (Lords.org) and ICC Playing Conditions URL mapping
MCC_LAW_URL_MAP = {
    1: ("Law 1 (The players)", "https://www.lords.org/mcc/the-laws-of-cricket/the-players"),
    2: ("Law 2 (The umpires)", "https://www.lords.org/mcc/the-laws-of-cricket/the-umpires"),
    3: ("Law 3 (The scorers)", "https://www.lords.org/mcc/the-laws-of-cricket/the-scorers"),
    4: ("Law 4 (The ball)", "https://www.lords.org/mcc/the-laws-of-cricket/the-ball"),
    5: ("Law 5 (The bat)", "https://www.lords.org/mcc/the-laws-of-cricket/the-bat"),
    6: ("Law 6 (The pitch)", "https://www.lords.org/mcc/the-laws-of-cricket/the-pitch"),
    7: ("Law 7 (The creases)", "https://www.lords.org/mcc/the-laws-of-cricket/the-creases"),
    8: ("Law 8 (The wickets)", "https://www.lords.org/mcc/the-laws-of-cricket/the-wickets"),
    9: ("Law 9 (Preparation and maintenance of the playing area)", "https://www.lords.org/mcc/the-laws-of-cricket/preparation-and-maintenance-of-the-playing-area"),
    10: ("Law 10 (Covering the pitch)", "https://www.lords.org/mcc/the-laws-of-cricket/covering-the-pitch"),
    11: ("Law 11 (Intervals)", "https://www.lords.org/mcc/the-laws-of-cricket/intervals"),
    12: ("Law 12 (Start of play; cessation of play)", "https://www.lords.org/mcc/the-laws-of-cricket/start-of-play-cessation-of-play"),
    13: ("Law 13 (Innings)", "https://www.lords.org/mcc/the-laws-of-cricket/innings"),
    14: ("Law 14 (The follow-on)", "https://www.lords.org/mcc/the-laws-of-cricket/the-follow-on"),
    15: ("Law 15 (Declaration and forfeiture)", "https://www.lords.org/mcc/the-laws-of-cricket/declaration-and-forfeiture"),
    16: ("Law 16 (The result)", "https://www.lords.org/mcc/the-laws-of-cricket/the-result"),
    17: ("Law 17 (The over)", "https://www.lords.org/mcc/the-laws-of-cricket/the-over"),
    18: ("Law 18 (Scoring runs)", "https://www.lords.org/mcc/the-laws-of-cricket/scoring-runs"),
    19: ("Law 19 (Boundaries)", "https://www.lords.org/mcc/the-laws-of-cricket/boundaries"),
    20: ("Law 20 (Dead ball)", "https://www.lords.org/mcc/the-laws-of-cricket/dead-ball"),
    21: ("Law 21 (No ball)", "https://www.lords.org/mcc/the-laws-of-cricket/no-ball"),
    22: ("Law 22 (Wide ball)", "https://www.lords.org/mcc/the-laws-of-cricket/wide-ball"),
    23: ("Law 23 (Bye and Leg bye)", "https://www.lords.org/mcc/the-laws-of-cricket/bye-and-leg-bye"),
    24: ("Law 24 (Fielder's absence; substitutes)", "https://www.lords.org/mcc/the-laws-of-cricket/fielders-absence-substitutes"),
    25: ("Law 25 (Batter's innings; runners)", "https://www.lords.org/mcc/the-laws-of-cricket/batters-innings-runners"),
    26: ("Law 26 (Practice on the field)", "https://www.lords.org/mcc/the-laws-of-cricket/practice-on-the-field"),
    27: ("Law 27 (The wicket-keeper)", "https://www.lords.org/mcc/the-laws-of-cricket/the-wicket-keeper"),
    28: ("Law 28 (The fielder / Protective equipment)", "https://www.lords.org/mcc/the-laws-of-cricket/the-fielder"),
    29: ("Law 29 (The wicket is broken)", "https://www.lords.org/mcc/the-laws-of-cricket/the-wicket-is-broken"),
    30: ("Law 30 (Batter out of his/her ground)", "https://www.lords.org/mcc/the-laws-of-cricket/batter-out-of-his-her-ground"),
    31: ("Law 31 (Appeals)", "https://www.lords.org/mcc/the-laws-of-cricket/appeals"),
    32: ("Law 32 (Bowled)", "https://www.lords.org/mcc/the-laws-of-cricket/bowled"),
    33: ("Law 33 (Caught)", "https://www.lords.org/mcc/the-laws-of-cricket/caught"),
    34: ("Law 34 (Hit the ball twice)", "https://www.lords.org/mcc/the-laws-of-cricket/hit-the-ball-twice"),
    35: ("Law 35 (Hit wicket)", "https://www.lords.org/mcc/the-laws-of-cricket/hit-wicket"),
    36: ("Law 36 (Leg before wicket)", "https://www.lords.org/mcc/the-laws-of-cricket/leg-before-wicket"),
    37: ("Law 37 (Obstructing the field)", "https://www.lords.org/mcc/the-laws-of-cricket/obstructing-the-field"),
    38: ("Law 38 (Run out)", "https://www.lords.org/mcc/the-laws-of-cricket/run-out"),
    39: ("Law 39 (Stumped)", "https://www.lords.org/mcc/the-laws-of-cricket/stumped"),
    40: ("Law 40 (Timed out)", "https://www.lords.org/mcc/the-laws-of-cricket/timed-out"),
    41: ("Law 41 (Unfair play)", "https://www.lords.org/mcc/the-laws-of-cricket/unfair-play"),
    42: ("Law 42 (Players' conduct)", "https://www.lords.org/mcc/the-laws-of-cricket/players-conduct"),
}


def get_dynamic_rule_link(law_identifier: str = "", *args, **kwargs) -> str:
    law_str = str(law_identifier).lower()
    if args:
        law_str += " " + " ".join(str(a).lower() for a in args)
    if "40" in law_str or "timed out" in law_str or "mathews" in law_str:
        return "https://www.lords.org/mcc/the-laws-of-cricket/timed-out"
    elif "36" in law_str or "lbw" in law_str:
        return "https://www.lords.org/mcc/the-laws-of-cricket/leg-before-wicket"
    elif "34" in law_str or "twice" in law_str:
        return "https://www.lords.org/mcc/the-laws-of-cricket/hit-the-ball-twice"
    elif "33" in law_str or "caught" in law_str or "catch" in law_str:
        return "https://www.lords.org/mcc/the-laws-of-cricket/caught"
    elif "22" in law_str or "wide" in law_str:
        return "https://www.lords.org/mcc/the-laws-of-cricket/wide-ball"
    elif "20" in law_str or "dead" in law_str:
        return "https://www.lords.org/mcc/the-laws-of-cricket/dead-ball"
    elif "21" in law_str or "no ball" in law_str:
        return "https://www.lords.org/mcc/the-laws-of-cricket/no-ball"
    elif "19" in law_str or "boundary" in law_str or "boundaries" in law_str:
        return "https://www.lords.org/mcc/the-laws-of-cricket/boundaries"
    elif "28" in law_str or "helmet" in law_str or "equipment" in law_str:
        return "https://www.lords.org/mcc/the-laws-of-cricket/fielders-equipment"
    elif "31" in law_str or "appeal" in law_str:
        return "https://www.lords.org/mcc/the-laws-of-cricket/appeals"
    elif "38" in law_str or "run out" in law_str or "mankad" in law_str:
        return "https://www.lords.org/mcc/the-laws-of-cricket/run-out"
    return "https://www.lords.org/mcc/the-laws-of-cricket"


def format_helpful_links_section(
    top_source: Optional[Dict[str, Any]] = None,
    query: str = ""
) -> str:
    """
    Builds the 'Helpful Links / Official Reference' section dynamically with
    the topic-specific direct URL.
    """
    law_label = top_source.get("law_number", "Official Law") if top_source else "MCC Law"
    sec_title = top_source.get("section_title", "") if top_source else ""
    rule_url = get_dynamic_rule_link(f"{law_label} {sec_title} {query}")

    return (
        f"---\n"
        f"### 💡 Helpful Links / Official Reference\n\n"
        f"- 📌 **Read Official {law_label} Clause:** [{rule_url}]({rule_url})\n"
        f"- 🔑 **Google AI Studio API Portal:** [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)\n"
        f"- 📜 **ICC Official Rules & Regulations:** [https://www.icc-cricket.com/about/cricket/rules-and-regulations/playing-conditions](https://www.icc-cricket.com/about/cricket/rules-and-regulations/playing-conditions)\n"
        f"- 🌐 **MCC Official Laws Hub:** [https://www.lords.org/mcc/the-laws-of-cricket](https://www.lords.org/mcc/the-laws-of-cricket)"
    )

GUARDRAIL_FALLBACK_MESSAGE = "I could not find a specific cricket rule covering this in the official laws."

CRICKET_RAG_SYSTEM_PROMPT = """You are the "Cricket Rules AI Assistant", an expert, authoritative, and strictly grounded rules adjudicator on the official Marylebone Cricket Club (MCC) Laws of Cricket and ICC Playing Conditions.

Your task is to answer user queries about cricket laws accurately and comprehensively using the provided official law context snippets and any attached visual scenario diagram.

STRICT GROUNDING & DUAL OUTPUT REQUIREMENTS:
1. COMPREHENSIVE TEXTUAL EXPLANATION:
   You must ALWAYS write a complete, detailed, and thorough textual rule explanation covering the rule step-by-step with all conditions, penalties, dead-ball triggers, and umpire procedures. You must NEVER replace the textual rules with an image alone or provide only an abbreviated summary.
2. CITATIONS:
   ALWAYS cite the specific Law Number and Section in your output (e.g., "According to MCC Law 36.1...", "Under MCC Law 28.3.1...", "Per ICC Appendix - Super Over Procedure...").
3. VISUAL EXPLAINER INTEGRATION:
   If a visual scenario explainer is provided in the context, explicitly and seamlessly reference the visual diagram in your explanation (e.g., "As illustrated in the diagram below...", "As shown in the [Title] diagram below..."), explaining how the visual diagram (crease markings, trajectory lines, impact zones, or field layouts) reinforces the official law.
4. OFFICIAL TOPIC-SPECIFIC LINKS & API GUIDANCE:
   Under "### 💡 Helpful Links / Official Reference", format the rule reference link dynamically for the specific law:
   - 📌 Read Official Law [Law Number] Clause: [Topic Specific Direct URL]
   Always provide the direct, topic-specific link for the rule (such as the specific Law page on Lords.org) rather than a generic landing page, along with:
   - 🔑 Google AI Studio API Portal: https://aistudio.google.com/app/apikey
   - 📜 ICC Official Rules & Regulations: https://www.icc-cricket.com/about/cricket/rules-and-regulations/playing-conditions
5. HALLUCINATION GUARDRAIL:
   If the query is unrelated to cricket rules or API setup, asks about a non-cricket sport, or if the provided context does NOT contain information to answer the question, you MUST respond EXACTLY with:
   "I could not find a specific cricket rule covering this in the official laws."
   Do NOT make up any rules, extrapolate, or guess outside the provided context.
"""


def get_chroma_collection(collection_name: str = COLLECTION_NAME, vector_path: Path = VECTOR_DIR):
    """Load a ChromaDB collection by name."""
    from src.ingest import get_embedding_function
    
    if not vector_path.exists():
        raise FileNotFoundError(
            f"Vector store directory not found at {vector_path.resolve()}. "
            "Please run 'python src/ingest.py' first."
        )

    embedding_func = get_embedding_function()
    client = chromadb.PersistentClient(path=str(vector_path))
    collection = client.get_collection(
        name=collection_name,
        embedding_function=embedding_func
    )
    return collection


def retrieve_relevant_laws(query: str, k: int = 2) -> List[Dict[str, Any]]:
    """Retrieve top-k relevant cricket law snippets from ChromaDB with hybrid re-ranking."""
    collection = get_chroma_collection(COLLECTION_NAME)
    fetch_k = max(k * 4, 12)
    results = collection.query(
        query_texts=[query],
        n_results=fetch_k,
        include=["documents", "metadatas", "distances"]
    )

    retrieved_items = []
    if results and "documents" in results and results["documents"]:
        docs = results["documents"][0]
        metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
        distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)

        q_words = set(re.findall(r'\b\w+\b', query.lower()))
        stop_words = {"what", "are", "the", "for", "an", "a", "is", "of", "in", "and", "how", "to", "does", "rules", "rule"}
        significant_q_words = {w for w in q_words if w not in stop_words and len(w) > 2}

        scored_items = []
        for doc, meta, dist in zip(docs, metas, distances):
            law_num = meta.get("law_number", "Unknown Law")
            sec_title = meta.get("section_title", "Unknown Section")
            text_lower = doc.lower()
            title_lower = f"{law_num} {sec_title}".lower()

            adjusted_dist = dist
            # Boost if query keywords match title or text
            title_matches = sum(1 for w in significant_q_words if w in title_lower)
            text_matches = sum(1 for w in significant_q_words if w in text_lower)
            adjusted_dist -= (title_matches * 0.35) + (text_matches * 0.05)

            scored_items.append((adjusted_dist, {
                "text": doc,
                "metadata": meta,
                "distance": dist,
                "score": adjusted_dist,
                "law_number": law_num,
                "section_title": sec_title,
                "source": meta.get("source", "mcc_cricket_laws.txt")
            }))

        scored_items.sort(key=lambda x: x[0])
        retrieved_items = [item[1] for item in scored_items[:k]]

    return retrieved_items


def retrieve_visual_scenario(query: str, max_distance: float = 1.85) -> Optional[Dict[str, Any]]:
    """
    Search the visual_scenarios database to retrieve the best visual explainer.
    Uses hybrid scoring (vector distance + scenario keyword alignment) to select
    the most relevant visual explainer.
    """
    try:
        collection = get_chroma_collection(VISUAL_COLLECTION_NAME)
    except Exception:
        return None

    results = collection.query(
        query_texts=[query],
        n_results=15,
        include=["documents", "metadatas", "distances"]
    )

    if not results or not results.get("metadatas") or not results["metadatas"][0]:
        return None

    metas = results["metadatas"][0]
    distances = results["distances"][0] if results.get("distances") else [1.0] * len(metas)

    q_lower = query.lower()

    # Rule-specific scenario keyword mappings
    KEYWORD_MAPPINGS = [
        (["lbw", "leg before wicket", "pad", "pitching in line"], "lbw_hawkeye_projection.png"),
        (["helmet", "resting helmet", "ground helmet", "law 28.3"], "dead_ball_helmet_ground.png"),
        (["dead ball", "boundary touch", "cease to be dead"], "dead_ball_boundary_touch.png"),
        (["foot fault", "overstepping", "popping crease", "front foot no ball"], "no_ball_foot_fault.png"),
        (["waist", "full toss", "beamer", "dangerous bowling"], "no_ball_waist_high_full_toss.png"),
        (["powerplay", "30-yard", "30 yard", "fielding restriction", "inner circle"], "powerplay_fielding_restrictions.png"),
        (["mankad", "non-striker", "backing up", "leaving crease early"], "mankad_non_striker_run_out.png"),
        (["relay catch", "airborne", "boundary catch", "catch beyond boundary", "boundary relay"], "fair_catch_boundary_relay.png"),
        (["stumped vs run out", "stumped or run out", "stumped", "run out difference"], "stumped_vs_run_out.png"),
        (["drs", "umpire's call", "umpires call", "ball tracking", "review"], "drs_umpires_call_zones.png"),
        (["super over", "tied match", "tie breaker", "boundary countback"], "super_over_procedure.png"),
        (["obstructing", "wilful", "deliberate distraction", "blocking throw"], "obstructing_the_field.png"),
        (["timed out", "timed-out", "mathews", "angelo mathews", "broken strap", "helmet strap", "2 minutes", "3 minutes", "law 40"], "timed_out_law40.png"),
        (["hit the ball twice", "hit twice", "struck twice", "ball hit twice", "defending wicket", "law 34"], "hit_ball_twice_law34.png"),
        (["wide ball", "wide", "tramline", "tramlines", "leg side wide", "passing wide", "law 22"], "wide_ball_variations_law22.png")
    ]

    best_item = None
    best_score = float("inf")

    for meta, dist in zip(metas, distances):
        fname = meta.get("file_name", "")
        score = dist
        for keywords, target_fname in KEYWORD_MAPPINGS:
            if target_fname == fname and any(kw in q_lower for kw in keywords):
                score -= 0.6  # Relevance boost
                break
        
        if score < best_score:
            best_score = score
            best_item = (meta, dist)

    if best_item and best_item[1] <= max_distance:
        meta, dist = best_item
        full_path = meta.get("full_path", "")
        if not full_path or not Path(full_path).exists():
            full_path = str(ROOT_DIR / meta.get("file_path", ""))

        return {
            "image_id": meta.get("image_id", ""),
            "file_name": meta.get("file_name", ""),
            "file_path": meta.get("file_path", ""),
            "full_path": full_path,
            "title": meta.get("title", ""),
            "law_reference": meta.get("law_reference", ""),
            "description": meta.get("description", ""),
            "distance": dist
        }

    return None


def format_context_for_prompt(sources: List[Dict[str, Any]]) -> str:
    """Format retrieved snippets into a clean string for the LLM prompt."""
    context_blocks = []
    for i, s in enumerate(sources, 1):
        law_num = s.get("law_number", f"Section {i}")
        title = s.get("section_title", "")
        text = s.get("text", "").strip()
        context_blocks.append(f"--- [Snippet {i}] {law_num} | {title} ---\n{text}")
    return "\n\n".join(context_blocks)


def call_llm(
    query: str,
    context: str,
    visual_scenario: Optional[Dict[str, Any]] = None,
    top_source: Optional[Dict[str, Any]] = None,
    api_key: Optional[str] = None,
    model_name: str = "gemini-1.5-flash"
) -> str:
    """
    Synthesize a grounded multimodal answer using Google Gemini.
    """
    key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    vis_context = ""
    if visual_scenario:
        vis_context = (
            f"\n\nATTACHED VISUAL EXPLAINER:\n"
            f"Title: {visual_scenario['title']} ({visual_scenario['law_reference']})\n"
            f"Visual Details: {visual_scenario['description']}\n"
            f"Explicitly reference this diagram in your explanation."
        )

    rule_url = get_dynamic_rule_link(
        f"{top_source.get('law_number', '')} {top_source.get('section_title', '')} {query}" if top_source else query
    )
    law_label = top_source.get("law_number", "Official Law") if top_source else "MCC Law"
    rule_link_context = f"\n\nTOPIC-SPECIFIC OFFICIAL RULE LINK:\n📌 Read Official {law_label} Clause: {rule_url}"

    if key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=key)

            user_prompt = f"""OFFICIAL CRICKET LAWS CONTEXT:
{context}{vis_context}{rule_link_context}

USER QUESTION:
{query}

INSTRUCTIONS:
1. Write a comprehensive, grounded explanation explaining the law step-by-step, citing the exact MCC Law number or ICC clause in detail. You must NEVER replace the textual rules with an image alone.
2. If a visual scenario diagram is provided above, explicitly reference the visual diagram (e.g., "As illustrated in the diagram below...").
3. In your response under a "### 💡 Helpful Links / Official Reference" section at the end, format the link dynamically:
   - 📌 **Read Official {law_label} Clause:** [{rule_url}]({rule_url})
   - 🔑 **Google AI Studio API Portal:** https://aistudio.google.com/app/apikey
   - 📜 **ICC Official Rules & Regulations:** https://www.icc-cricket.com/about/cricket/rules-and-regulations/playing-conditions"""

            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=CRICKET_RAG_SYSTEM_PROMPT
            )
            response = model.generate_content(user_prompt)
            return response.text.strip()
        except Exception as e:
            print(f"[Warning] LLM call with {model_name} failed: {e}. Falling back to rule-grounded response.")
            try:
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-pro",
                    system_instruction=CRICKET_RAG_SYSTEM_PROMPT
                )
                response = model.generate_content(user_prompt)
                return response.text.strip()
            except Exception:
                pass

    return generate_local_grounded_answer(query, context, visual_scenario, top_source)


OFFICIAL_LINKS_INFO = """### 🔗 Official Portals & Helpful Links

Here are the official links:

- 🔑 **Google AI Studio API Portal:** [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)  
  *Generate your free Google Gemini API key from Google AI Studio to power real-time AI synthesis. Paste it in the sidebar or save as `GEMINI_API_KEY` in `.env`.*

- 📜 **ICC Official Rules & Regulations:** [https://www.icc-cricket.com/about/cricket/rules-and-regulations/playing-conditions](https://www.icc-cricket.com/about/cricket/rules-and-regulations/playing-conditions)  
  *Access official source documents for updated ICC Test, ODI, T20I playing conditions and MCC Laws.*

- 🌐 **MCC Official Laws Hub:** [https://www.lords.org/mcc/the-laws-of-cricket](https://www.lords.org/mcc/the-laws-of-cricket)  
  *Official Marylebone Cricket Club (MCC) home for all 42 Laws of Cricket.*"""


def check_link_or_key_query(query: str) -> Optional[str]:
    """Check if the query asks about obtaining an API key or official rule links."""
    q = query.lower()
    is_api_query = any(k in q for k in [
        "api key", "gemini key", "get key", "google key", "where to get key",
        "how to get api key", "how do i get an api key", "api token"
    ])
    is_link_query = any(k in q for k in [
        "official rule link", "official rule links", "rules link", "rule links",
        "link for rules", "link to icc", "link to mcc", "rules website",
        "playing conditions link", "official link", "official links", "official source"
    ])
    if is_api_query or is_link_query:
        return OFFICIAL_LINKS_INFO
    return None


def generate_local_grounded_answer(
    query: str,
    context: str,
    visual_scenario: Optional[Dict[str, Any]] = None,
    top_source: Optional[Dict[str, Any]] = None
) -> str:
    """
    Local fallback synthesizer for situations where an LLM API key has not been configured.
    Ensures strict grounding, citations, and visual explainer callouts.
    """
    q_lower = query.lower()
    
    # Check link queries first
    link_resp = check_link_or_key_query(query)
    if link_resp:
        return link_resp

    # Check obvious out-of-domain keywords (football, basketball, politics, cooking, etc.)
    non_cricket_terms = ["football", "soccer", "basketball", "tennis", "rugby", "baseball", "recipe", "weather", "offside"]
    if any(term in q_lower for term in non_cricket_terms) and "cricket" not in q_lower:
        return GUARDRAIL_FALLBACK_MESSAGE

    if not context or len(context.strip()) < 20:
        return GUARDRAIL_FALLBACK_MESSAGE

    # Construct a grounded summary from the top retrieved snippet
    snippets = context.split("--- [Snippet")
    relevant_content = snippets[1] if len(snippets) > 1 else context
    
    lines = [line.strip() for line in relevant_content.split("\n") if line.strip()]
    header = lines[0] if lines else "MCC Cricket Law"
    body = "\n".join(lines[1:])

    vis_callout = ""
    if visual_scenario:
        vis_callout = (
            f"\n\n📸 **Visual Explainer Reference**:\n"
            f"As illustrated in the **[{visual_scenario['title']}]** diagram below, "
            f"{visual_scenario['description']}"
        )
    
    links_section = format_helpful_links_section(top_source, query)

    return (
        f"**Official Rule Guidance**:\n\n"
        f"According to the official Laws of Cricket recorded in **{header}**:\n\n"
        f"{body}"
        f"{vis_callout}\n\n"
        f"{links_section}"
    )


def query_cricket_rules(
    query: str,
    k: int = 2,
    api_key: Optional[str] = None,
    model_name: str = "gemini-1.5-flash"
) -> Dict[str, Any]:
    """
    Full Visual RAG pipeline:
    1. Check for API key / official links inquiries
    2. Primary search: Retrieve top-k (k=2) law snippets from 'cricket_laws'
    3. Secondary search: Retrieve top visual explainer from 'visual_scenarios'
    4. Guardrail check
    5. Generate multimodal grounded response
    6. Return structured response with text, sources, and visual asset
    """
    clean_query = query.strip()
    if not clean_query:
        return {
            "answer": "Please ask a question regarding cricket rules.",
            "sources": [],
            "visual_scenario": None,
            "dynamic_link": None,
            "guardrail_triggered": False
        }

    # Intercept API key / link inquiries directly with accurate resources
    direct_link_resp = check_link_or_key_query(clean_query)
    if direct_link_resp:
        return {
            "answer": direct_link_resp,
            "sources": [],
            "visual_scenario": None,
            "dynamic_link": None,
            "guardrail_triggered": False
        }

    # 1. Primary Retrieval: Text Laws (k=2)
    try:
        sources = retrieve_relevant_laws(clean_query, k=k)
    except Exception as e:
        return {
            "answer": f"Error accessing cricket rules vector store: {str(e)}. Please run 'python src/ingest.py' first.",
            "sources": [],
            "visual_scenario": None,
            "dynamic_link": None,
            "guardrail_triggered": False
        }

    if not sources:
        return {
            "answer": GUARDRAIL_FALLBACK_MESSAGE,
            "sources": [],
            "visual_scenario": None,
            "dynamic_link": None,
            "guardrail_triggered": True
        }

    # 2. Secondary Retrieval: Visual Scenario
    visual_scenario = retrieve_visual_scenario(clean_query)

    # 3. Format Context
    context = format_context_for_prompt(sources)
    top_source = sources[0] if sources else None

    # 4. Synthesize with LLM or local fallback
    answer = call_llm(
        clean_query,
        context,
        visual_scenario=visual_scenario,
        top_source=top_source,
        api_key=api_key,
        model_name=model_name
    )

    # 5. Check if guardrail triggered
    is_guardrail = GUARDRAIL_FALLBACK_MESSAGE.lower() in answer.lower()
    if is_guardrail:
        visual_scenario = None  # Do not attach visual explainer for out-of-domain queries
        dynamic_link = None
    else:
        dynamic_link = get_dynamic_rule_link(
            f"{top_source.get('law_number', '')} {top_source.get('section_title', '')} {clean_query}" if top_source else clean_query
        )
        # Ensure the dynamic topic link is always cleanly formatted in the answer if missing
        if dynamic_link not in answer:
            answer = f"{answer}\n\n{format_helpful_links_section(top_source, clean_query)}"

    return {
        "answer": answer,
        "sources": sources,
        "visual_scenario": visual_scenario,
        "context_used": context,
        "dynamic_link": dynamic_link,
        "guardrail_triggered": is_guardrail
    }


if __name__ == "__main__":
    test_q = "What happens if the ball hits the helmet resting on the ground behind the keeper?"
    print(f"Testing Query: {test_q}")
    res = query_cricket_rules(test_q, k=2)
    print("\n--- Answer ---")
    print(res["answer"])
    print(f"\n--- Retrieved Sources ({len(res['sources'])}) ---")
    for s in res["sources"]:
        print(f"[{s['law_number']}] {s['section_title']} (dist: {s['distance']:.3f})")
    print(f"\n--- Matched Visual Explainer ---")
    if res["visual_scenario"]:
        print(f"Title: {res['visual_scenario']['title']}")
        print(f"File: {res['visual_scenario']['file_path']}")
        print(f"Distance: {res['visual_scenario']['distance']:.3f}")
    else:
        print("None")
