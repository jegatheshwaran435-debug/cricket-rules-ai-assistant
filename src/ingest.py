import os
import re
import sys
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

import numpy as np
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
VECTOR_DIR = Path(__file__).resolve().parent.parent / "vectorstore"
DATA_IMAGES_DIR = Path(__file__).resolve().parent.parent / "data" / "images"

COLLECTION_NAME = "cricket_laws"
VISUAL_COLLECTION_NAME = "cricket_visual_scenarios"

from chromadb import EmbeddingFunction, Documents, Embeddings


class RobustLocalEmbeddingFunction(EmbeddingFunction):
    """
    Deterministic, zero-network fallback embedding function.
    Produces 384-dimensional normalized dense vectors using sub-token and word feature hashing.
    Zero external download dependencies, zero timeouts, lightning fast.
    """
    def __init__(self, dim: int = 384):
        self.dim = dim

    def name(self) -> str:
        return "robust_local_cricket_embedding"

    def __call__(self, input: Documents) -> Embeddings:
        embeddings = []
        for text in input:
            vec = np.zeros(self.dim, dtype=np.float32)
            tokens = re.findall(r"[a-z0-9_]+", text.lower())
            for t in tokens:
                # Primary token hash
                idx1 = int(hashlib.md5(t.encode("utf-8")).hexdigest()[:8], 16) % self.dim
                vec[idx1] += 1.0
                # Sub-word feature hash
                if len(t) >= 4:
                    idx2 = int(hashlib.sha256(t[:4].encode("utf-8")).hexdigest()[:8], 16) % self.dim
                    vec[idx2] += 0.5

            # L2 normalize for cosine similarity
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            embeddings.append(vec.tolist())
        return embeddings


class GeminiEmbeddingWrapper(EmbeddingFunction):
    """Wrapper around Google Gemini embedding API."""
    def __init__(self, api_key: str, model_name: str = "models/text-embedding-004"):
        import google.generativeai as genai
        self.api_key = api_key
        self.model_name = model_name
        genai.configure(api_key=api_key)
        self.genai = genai

    def name(self) -> str:
        return "gemini_cricket_embedding"

    def __call__(self, input: Documents) -> Embeddings:
        embeddings = []
        for text in input:
            try:
                res = self.genai.embed_content(
                    model=self.model_name,
                    content=text,
                    task_type="retrieval_document"
                )
                embeddings.append(res["embedding"])
            except Exception as e:
                print(f"[Warning] Gemini embedding failed: {e}. Falling back to local vector.")
                local_fallback = RobustLocalEmbeddingFunction()
                return local_fallback(input)
        return embeddings


def get_embedding_function(api_key: Optional[str] = None):
    """
    Returns the appropriate embedding function:
    - GeminiEmbeddingWrapper if api_key or GEMINI_API_KEY/GOOGLE_API_KEY is available.
    - RobustLocalEmbeddingFunction for ultra-fast, zero-network local execution.
    """
    key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if key and len(key.strip()) > 10:
        try:
            return GeminiEmbeddingWrapper(api_key=key.strip())
        except Exception as e:
            print(f"[Warning] Failed to initialize Gemini embeddings: {e}")

    return RobustLocalEmbeddingFunction()


# ==============================================================================
# VISUAL SCENARIOS DATASET (12 Infographics Metadata)
# ==============================================================================
VISUAL_SCENARIOS_DATA = [
    {
        "id": "vis_lbw_hawkeye",
        "file_name": "lbw_hawkeye_projection.png",
        "title": "Hawkeye LBW Ball Tracking & Impact Zone Explainer",
        "law_reference": "MCC Law 36",
        "text": "LBW Leg Before Wicket Hawkeye ball tracking projection pitching in line impact in line hitting wickets stump height pad contact genuine attempt no shot offered outside off outside leg",
        "description": "Hawkeye visual explainer showing ball pitching in line, striking pad in line between wicket and wicket, and projected trajectory hitting stumps with blue impact zone and red wickets zone."
    },
    {
        "id": "vis_dead_ball_helmet",
        "file_name": "dead_ball_helmet_ground.png",
        "title": "Ball Striking Fielder's Helmet Resting on Ground",
        "law_reference": "MCC Law 28.3",
        "text": "ball hits helmet resting on ground behind keeper wicketkeeper protective equipment not in use dead ball 5 penalty runs batting side extras boundary",
        "description": "Diagram illustrating the ball striking a helmet placed on the ground behind the wicketkeeper, triggering an immediate dead ball and awarding 5 penalty runs to the batting side."
    },
    {
        "id": "vis_dead_ball_boundary",
        "file_name": "dead_ball_boundary_touch.png",
        "title": "Dead Ball & Boundary Interception Regulations",
        "law_reference": "MCC Law 20 & Law 19",
        "text": "dead ball boundary touch fielder in contact with boundary cushion while touching ball boundary 4 or 6 umpire dead ball signal settled in keeper hands cease to be dead",
        "description": "Visual guide covering dead ball boundary interception and standard conditions when the ball becomes dead or comes into play."
    },
    {
        "id": "vis_no_ball_foot",
        "file_name": "no_ball_foot_fault.png",
        "title": "Fair Delivery Crease Regulations (Foot Fault No-Ball)",
        "law_reference": "MCC Law 21.5",
        "text": "no ball front foot fault overstepping popping crease return crease back foot cutting return crease fair delivery landing heel grounded raised",
        "description": "Technical diagram demonstrating front foot overstepping beyond popping crease line and back foot crossing the return crease resulting in a No Ball."
    },
    {
        "id": "vis_no_ball_beamer",
        "file_name": "no_ball_waist_high_full_toss.png",
        "title": "Waist-High Full Toss (Dangerous Beamer Delivery)",
        "law_reference": "MCC Law 21.9",
        "text": "no ball waist high full toss beamer passing striker above waist height without pitching upright stance free hit dangerous bowling pace spin",
        "description": "Visual trajectory showing a ball delivered on the full passing the striker above waist height when standing upright at the popping crease."
    },
    {
        "id": "vis_powerplay_fielding",
        "file_name": "powerplay_fielding_restrictions.png",
        "title": "ODI & T20I Powerplay & 30-Yard Circle Restrictions",
        "law_reference": "ICC Playing Conditions",
        "text": "powerplay fielding restrictions 30 yard circle inner ring mandatory powerplay max 2 fielders outside circle overs 1 to 10 t20i overs 1 to 6 field placement death overs",
        "description": "Field map diagram illustrating the 30-yard inner circle and fielder distribution limits across Powerplay 1, Powerplay 2, and death overs."
    },
    {
        "id": "vis_mankad_run_out",
        "file_name": "mankad_non_striker_run_out.png",
        "title": "Running Out the Non-Striker Leaving Ground Early (Mankad)",
        "law_reference": "MCC Law 38.3",
        "text": "mankad running out non striker leaving crease early before bowler delivery release point run out law 38 fair dismissal backing up stumps broken",
        "description": "Crease diagram showing bowler stopping before delivery release point to run out a non-striker who has prematurely backed up out of their ground."
    },
    {
        "id": "vis_boundary_relay",
        "file_name": "fair_catch_boundary_relay.png",
        "title": "Boundary Rope Contact & Airborne Relay Catch",
        "law_reference": "MCC Law 33.2",
        "text": "fair catch boundary rope contact airborne relay catch first contact inside ground cushion jump toss ball partner complete firm control six boundary",
        "description": "Illustrated boundary relay catch requirements: first contact must be inside the field of play, with no contact with the boundary while holding the ball."
    },
    {
        "id": "vis_stumped_vs_run_out",
        "file_name": "stumped_vs_run_out.png",
        "title": "Stumped (Law 39) vs Run Out (Law 38) Distinction",
        "law_reference": "MCC Laws 38 & 39",
        "text": "stumped vs run out difference wicket keeper action batter out of ground not attempting a run sliding bat bounce out of crease wide delivery",
        "description": "Side-by-side comparison between Out Stumped (batter not attempting run, keeper breaks wicket) and Out Run Out (batter attempting run, any fielder breaks wicket)."
    },
    {
        "id": "vis_drs_umpires_call",
        "file_name": "drs_umpires_call_zones.png",
        "title": "DRS Ball Tracking & Umpire's Call Zones Explainer",
        "law_reference": "ICC DRS Protocol",
        "text": "drs decision review system umpires call hawkeye ball tracking pitching in line impact zone wicket hitting 50 percent ball rule review retained stand",
        "description": "Hawk-Eye DRS technical diagram detailing the 50% ball threshold for Pitching, Impact, and Wickets Hitting, explaining when Umpire's Call applies."
    },
    {
        "id": "vis_super_over",
        "file_name": "super_over_procedure.png",
        "title": "ICC Super Over Tie-Breaker Procedure",
        "law_reference": "ICC Appendix",
        "text": "super over tie breaker tied match knockout playoff 6 legal deliveries 2 wickets boundary countback abolished subsequent super over winner",
        "description": "Flowchart of the ICC Super Over procedure: 6 legal balls, 2 wickets maximum, with mandatory subsequent Super Overs if tied."
    },
    {
        "id": "vis_obstructing_field",
        "file_name": "obstructing_the_field.png",
        "title": "Obstructing the Field: Wilful Diversion vs Accidental Contact",
        "law_reference": "MCC Law 37",
        "text": "obstructing the field deliberate distraction wilful diversion blocking throw bat interception returning ball avoid injury accidental deflection out",
        "description": "Visual breakdown of wilful obstruction of fielder's throw (Out) versus accidental deflection or action taken to avoid injury (Not Out)."
    },
    {
        "id": "vis_timed_out",
        "file_name": "timed_out_law40.png",
        "title": "Timed Out Regulations & Mandatory Timelines",
        "law_reference": "MCC Law 40",
        "text": "timed out law 40 angelo mathews broken helmet strap 2 minutes icc world cup 3 minutes mcc incoming batter ready to face delivery appeal fielding captain",
        "description": "Infographic explaining the Timed Out dismissal timeline (2-minute ICC vs 3-minute MCC rule), equipment delay procedures, and mandatory fielding appeal requirement."
    },
    {
        "id": "vis_hit_ball_twice",
        "file_name": "hit_ball_twice_law34.png",
        "title": "Hit the Ball Twice Adjudication Diagram",
        "law_reference": "MCC Law 34",
        "text": "hit the ball twice hit twice struck twice defend wicket defence of stumps lawful second strike attempt to score run dead ball out",
        "description": "Adjudication diagram contrasting lawful second strike solely in defense of wicket against unlawful second hit attempting runs or preventing catch."
    },
    {
        "id": "vis_wide_ball",
        "file_name": "wide_ball_variations_law22.png",
        "title": "Wide Ball Tramlines & Judging Criteria Explainer",
        "law_reference": "MCC Law 22",
        "text": "wide ball tramline off side tramline 17 inches return crease leg side wide zero margin batter movement switch hit 1 penalty run extra delivery",
        "description": "Pitch diagram detailing off-side tramlines, leg-side zero-margin wide guidelines in limited overs, batter movement compensation, and penalty runs."
    }
]


def extract_text_from_file(file_path: Path) -> str:
    """Extract text from text files or PDF files."""
    suffix = file_path.suffix.lower()
    if suffix in [".txt", ".md"]:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    elif suffix == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(file_path))
            pages_text = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                pages_text.append(f"--- Page {i + 1} ---\n{text}")
            return "\n\n".join(pages_text)
        except Exception as e:
            print(f"[Error] Failed to read PDF {file_path}: {e}")
            return ""
    else:
        print(f"[Warning] Unsupported file type: {suffix} for {file_path}")
        return ""


def detect_law_metadata(chunk_text: str) -> Dict[str, str]:
    """Detect Law number and section title from chunk text."""
    law_match = re.search(r"(?:MCC\s+)?LAW\s+(\d+[A-Za-z]?(?:\.\d+)*)", chunk_text, re.IGNORECASE)
    law_num = f"Law {law_match.group(1)}" if law_match else "General Cricket Law"
    
    if "SUPER OVER" in chunk_text.upper():
        law_num = "ICC Super Over Procedure"
    elif "DECISION REVIEW SYSTEM" in chunk_text.upper() or "DRS" in chunk_text.upper():
        law_num = "ICC Decision Review System (DRS)"

    lines = [line.strip() for line in chunk_text.strip().split("\n") if line.strip()]
    first_meaningful_line = lines[0] if lines else "Cricket Rule Section"
    first_meaningful_line = first_meaningful_line.replace("=", "").replace("#", "").strip()
    
    return {
        "law_number": law_num,
        "section_title": first_meaningful_line[:100]
    }


def chunk_cricket_laws(text: str, source_filename: str, chunk_size: int = 800, chunk_overlap: int = 150) -> List[Dict[str, Any]]:
    """Split text into logical chunks preserving law contexts and subclauses."""
    sections = re.split(r"\n={10,}\n", text)
    chunks = []

    for sec in sections:
        sec = sec.strip()
        if not sec:
            continue
            
        if len(sec) <= chunk_size:
            meta = detect_law_metadata(sec)
            meta["source"] = source_filename
            chunks.append({
                "text": sec,
                "metadata": meta
            })
        else:
            subsections = re.split(r"\n(?=MCC Law \d|ICC Appendix|\bClause \d)", sec)
            for sub in subsections:
                sub = sub.strip()
                if not sub:
                    continue
                    
                if len(sub) <= chunk_size:
                    meta = detect_law_metadata(sub)
                    meta["source"] = source_filename
                    chunks.append({
                        "text": sub,
                        "metadata": meta
                    })
                else:
                    start = 0
                    while start < len(sub):
                        end = min(start + chunk_size, len(sub))
                        chunk_part = sub[start:end].strip()
                        if chunk_part:
                            meta = detect_law_metadata(chunk_part)
                            meta["source"] = source_filename
                            chunks.append({
                                "text": chunk_part,
                                "metadata": meta
                            })
                        if end == len(sub):
                            break
                        start += (chunk_size - chunk_overlap)

    return chunks


def build_vector_store(data_path: Path = DATA_DIR, vector_path: Path = VECTOR_DIR, api_key: Optional[str] = None) -> Tuple[int, int]:
    """Parses all documents in data/ and ingests them into ChromaDB (both text laws & visual scenarios)."""
    import chromadb
    
    print(f"[Ingest] Scanning documents in: {data_path.resolve()}")
    if not data_path.exists():
        data_path.mkdir(parents=True, exist_ok=True)
        print(f"[Ingest] Created directory: {data_path}")

    files = list(data_path.glob("*.txt")) + list(data_path.glob("*.pdf")) + list(data_path.glob("*.md"))
    if not files:
        print("[Ingest] No .txt, .pdf, or .md files found in data directory.")
        return 0, 0

    all_chunks: List[Dict[str, Any]] = []
    for file_path in files:
        print(f"[Ingest] Processing {file_path.name}...")
        raw_text = extract_text_from_file(file_path)
        if not raw_text.strip():
            print(f"[Ingest] Skipping empty file: {file_path.name}")
            continue
        file_chunks = chunk_cricket_laws(raw_text, source_filename=file_path.name)
        print(f"[Ingest] Created {len(file_chunks)} chunks for {file_path.name}")
        all_chunks.extend(file_chunks)

    if not all_chunks:
        print("[Ingest] No chunks generated from documents.")
        return 0, 0

    print(f"[Ingest] Initializing ChromaDB vector store at: {vector_path.resolve()}")
    vector_path.mkdir(parents=True, exist_ok=True)
    
    embedding_func = get_embedding_function(api_key=api_key)
    client = chromadb.PersistentClient(path=str(vector_path))
    
    # 1. Index Official Text Laws Collection
    try:
        client.delete_collection(name=COLLECTION_NAME)
        print(f"[Ingest] Cleared previous collection '{COLLECTION_NAME}'")
    except Exception:
        pass
        
    law_collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_func,
        metadata={"description": "MCC Laws of Cricket & ICC Playing Conditions Vector Store"}
    )

    documents = [c["text"] for c in all_chunks]
    metadatas = [c["metadata"] for c in all_chunks]
    ids = [f"law_chunk_{i+1:04d}" for i in range(len(all_chunks))]

    batch_size = 50
    for i in range(0, len(documents), batch_size):
        end = min(i + batch_size, len(documents))
        law_collection.add(
            documents=documents[i:end],
            metadatas=metadatas[i:end],
            ids=ids[i:end]
        )

    print(f"[Ingest] Successfully indexed {len(documents)} rule chunks into ChromaDB collection '{COLLECTION_NAME}'!")

    # 2. Index Visual Scenarios Collection
    try:
        client.delete_collection(name=VISUAL_COLLECTION_NAME)
        print(f"[Ingest] Cleared previous collection '{VISUAL_COLLECTION_NAME}'")
    except Exception:
        pass

    visual_collection = client.create_collection(
        name=VISUAL_COLLECTION_NAME,
        embedding_function=embedding_func,
        metadata={"description": "Cricket Rule Visual Scenarios & Infographics Vector Store"}
    )

    vis_docs = []
    vis_metas = []
    vis_ids = []

    for vis in VISUAL_SCENARIOS_DATA:
        img_rel_path = f"data/images/{vis['file_name']}"
        img_full_path = str(DATA_IMAGES_DIR / vis["file_name"])
        vis_docs.append(f"{vis['title']} {vis['law_reference']}: {vis['text']} - {vis['description']}")
        vis_metas.append({
            "image_id": vis["id"],
            "file_name": vis["file_name"],
            "file_path": img_rel_path,
            "full_path": img_full_path,
            "title": vis["title"],
            "law_reference": vis["law_reference"],
            "description": vis["description"]
        })
        vis_ids.append(vis["id"])

    visual_collection.add(
        documents=vis_docs,
        metadatas=vis_metas,
        ids=vis_ids
    )
    print(f"[Ingest] Successfully indexed {len(vis_docs)} visual infographics into ChromaDB collection '{VISUAL_COLLECTION_NAME}'!")

    return len(documents), len(vis_docs)


if __name__ == "__main__":
    law_cnt, vis_cnt = build_vector_store()
    print(f"[Done] Ingest complete: {law_cnt} rule chunks, {vis_cnt} visual scenarios indexed.")
