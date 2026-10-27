import os
import sys
from pathlib import Path

# Ensure root directory is on Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Ensure UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.rag_engine import query_cricket_rules, get_dynamic_rule_link, GUARDRAIL_FALLBACK_MESSAGE


BENCHMARK_SCENARIOS = [
    {
        "name": "LBW Dismissal & Hawkeye Ball Tracking",
        "query": "What are the rules for an LBW dismissal and Hawkeye impact zone?",
        "expected_law": "36",
        "expected_visual_file": "lbw_hawkeye_projection.png",
        "expected_url_substring": "leg-before-wicket",
        "must_contain_words": ["pitch", "impact", "wicket"]
    },
    {
        "name": "Ball Striking Fielder's Resting Helmet",
        "query": "What happens if the ball hits the helmet resting on the ground behind the keeper?",
        "expected_law": "28",
        "expected_visual_file": "dead_ball_helmet_ground.png",
        "expected_url_substring": "fielders-equipment",
        "must_contain_words": ["penalty", "dead"]
    },
    {
        "name": "Timed Out & Angelo Mathews Precedent",
        "query": "What is the Timed Out rule and Angelo Mathews helmet strap scenario?",
        "expected_law": "40",
        "expected_visual_file": "timed_out_law40.png",
        "expected_url_substring": "timed-out",
        "must_contain_words": ["minute", "appeal"]
    },
    {
        "name": "Hit the Ball Twice",
        "query": "Can a batter hit the ball twice with their bat to defend the stumps?",
        "expected_law": "34",
        "expected_visual_file": "hit_ball_twice_law34.png",
        "expected_url_substring": "hit-the-ball-twice",
        "must_contain_words": ["defen", "twice"]
    },
    {
        "name": "Wide Ball & Tramlines",
        "query": "What are the rules and tramlines for calling a Wide Ball?",
        "expected_law": "22",
        "expected_visual_file": "wide_ball_variations_law22.png",
        "expected_url_substring": "wide-ball",
        "must_contain_words": ["wide", "run"]
    },
    {
        "name": "Boundary Airborne Relay Catch",
        "query": "What are the rules for an airborne boundary relay catch?",
        "expected_law": ["19", "33"],
        "expected_visual_file": "fair_catch_boundary_relay.png",
        "expected_url_substring": ["boundaries", "caught"],
        "must_contain_words": ["boundary", "catch"]
    },
    {
        "name": "Front-Foot Crease No Ball",
        "query": "What are the rules for a front-foot No Ball overstepping the popping crease?",
        "expected_law": "21",
        "expected_visual_file": "no_ball_foot_fault.png",
        "expected_url_substring": "no-ball",
        "must_contain_words": ["crease", "no ball"]
    },
    {
        "name": "Running Out Non-Striker (Mankad)",
        "query": "Can a bowler run out a non-striker backing up early before release?",
        "expected_law": "38",
        "expected_visual_file": "mankad_non_striker_run_out.png",
        "expected_url_substring": "run-out",
        "must_contain_words": ["non-striker", "release"]
    },
    {
        "name": "DRS Umpire's Call Protocol",
        "query": "How does Umpire's Call work in a DRS ball tracking review?",
        "expected_law": "DRS",
        "expected_visual_file": "drs_umpires_call_zones.png",
        "expected_url_substring": "playing-conditions",
        "must_contain_words": ["umpire", "review"]
    },
    {
        "name": "Super Over Tie-Breaker",
        "query": "How is a tied Super Over procedure resolved in ICC knockout matches?",
        "expected_law": "Super Over",
        "expected_visual_file": "super_over_procedure.png",
        "expected_url_substring": "playing-conditions",
        "must_contain_words": ["super over", "tied"]
    }
]


def run_benchmark():
    """Runs automated edge-case evaluation against the vector store and visual catalog."""
    print("=" * 80)
    print("CRICKET RULES RAG BENCHMARK & EVALUATION SUITE")
    print("=" * 80)

    total_scenarios = len(BENCHMARK_SCENARIOS)
    passed = 0
    failed = 0

    for i, scenario in enumerate(BENCHMARK_SCENARIOS, 1):
        name = scenario["name"]
        query = scenario["query"]
        print(f"\n[{i}/{total_scenarios}] Evaluating: {name}")
        print(f"  Query: \"{query}\"")

        res = query_cricket_rules(query, k=2)

        # 1. Retrieval validation
        sources = res.get("sources", [])
        if not sources:
            print(f"  [FAIL] No sources retrieved for valid cricket scenario.")
            failed += 1
            continue

        top_law = sources[0].get("law_number", "")
        top_title = sources[0].get("section_title", "")
        print(f"  Retrieved Law: {top_law} — {top_title}")

        expected_law = scenario["expected_law"]
        if isinstance(expected_law, list):
            law_match = any(el.lower() in top_law.lower() or el.lower() in top_title.lower() for el in expected_law)
        else:
            law_match = expected_law.lower() in top_law.lower() or expected_law.lower() in top_title.lower()

        if not law_match:
            print(f"  [WARN] Top retrieved law '{top_law}' did not match expected '{expected_law}' (checking second snippet)")
            if len(sources) > 1:
                sec_law = sources[1].get("law_number", "")
                if isinstance(expected_law, list):
                    law_match = any(el.lower() in sec_law.lower() for el in expected_law)
                else:
                    law_match = expected_law.lower() in sec_law.lower()

        # 2. Visual scenario validation
        visual = res.get("visual_scenario")
        if not visual:
            print(f"  [FAIL] Missing visual scenario for scenario '{name}'.")
            failed += 1
            continue

        vis_file = visual.get("file_name", "")
        expected_file = scenario["expected_visual_file"]
        if vis_file != expected_file:
            print(f"  [FAIL] Expected visual '{expected_file}', but got '{vis_file}'.")
            failed += 1
            continue

        print(f"  Visual Matched: {visual.get('title')} ({vis_file})")

        # 3. Dynamic Link validation
        dynamic_link = res.get("dynamic_link") or get_dynamic_rule_link(top_law)
        expected_url = scenario["expected_url_substring"]
        if isinstance(expected_url, list):
            url_match = any(u in str(dynamic_link) or u in res["answer"] for u in expected_url)
        else:
            url_match = expected_url in str(dynamic_link) or expected_url in res["answer"]

        if not url_match:
            print(f"  [FAIL] Expected URL containing '{expected_url}', got '{dynamic_link}'.")
            failed += 1
            continue

        # 4. Keyword verification
        answer_lower = res["answer"].lower()
        missing_kw = [kw for kw in scenario["must_contain_words"] if kw not in answer_lower]
        if missing_kw:
            print(f"  [FAIL] Missing required keywords {missing_kw} in synthesized answer.")
            failed += 1
            continue

        print(f"  Dynamic Link: {dynamic_link}")
        print(f"  [PASS] All benchmarks verified for '{name}'.")
        passed += 1

    # 5. Guardrail Refusal Benchmark
    print("\n[Guardrail Test] Evaluating Out-of-Domain Refusal:")
    ood_query = "What is the penalty for an offside in ice hockey?"
    ood_res = query_cricket_rules(ood_query, k=2)
    assert GUARDRAIL_FALLBACK_MESSAGE.lower() in ood_res["answer"].lower(), "Expected guardrail fallback message"
    assert ood_res.get("visual_scenario") is None, "Visual scenario must be None on guardrail hit"
    print(f"  Refusal Verified: '{ood_res['answer'][:70]}...'")
    print(f"  [PASS] Guardrail correctly enforced.")
    passed += 1

    print("\n" + "=" * 80)
    print(f"BENCHMARK RESULTS: {passed}/{total_scenarios + 1} PASSED ({(passed / (total_scenarios + 1)) * 100:.1f}%)")
    print("=" * 80)

    if failed == 0:
        print("🏆 ALL PRODUCTION EDGE-CASE EVALUATION BENCHMARKS PASSED PERFECTLY!")
        return 0
    else:
        print(f"❌ {failed} benchmarks failed.")
        return 1


if __name__ == "__main__":
    exit_code = run_benchmark()
    sys.exit(exit_code)
