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


def test_helmet_on_ground_rule():
    query = "What happens if the ball hits the helmet resting on the ground behind the keeper?"
    res = query_cricket_rules(query, k=2)
    print(f"\n[Test 1] Query: {query}")
    print(f"Top Law Retrieved: {res['sources'][0]['law_number']}")
    print(f"Top Title: {res['sources'][0]['section_title']}")
    
    assert "28" in res['sources'][0]['law_number'] or "helmet" in res['sources'][0]['text'].lower(), \
        "Expected Law 28 / helmet rule in top retrieved sources"
    assert "5 penalty runs" in res['sources'][0]['text'].lower() or "dead" in res['sources'][0]['text'].lower(), \
        "Expected dead ball and 5 penalty runs in retrieved rule"
    
    # Visual Scenario Verification
    assert res.get("visual_scenario") is not None, "Expected a visual scenario for helmet on ground"
    assert "helmet" in res["visual_scenario"]["file_name"].lower(), \
        f"Expected helmet visual, got: {res['visual_scenario']['file_name']}"
    print(f"Visual Explainer Matched: {res['visual_scenario']['title']} ({res['visual_scenario']['file_name']})")
    print("[PASS] Test 1: Helmet on ground (Law 28.3) and visual explainer successfully verified.")


def test_lbw_rule():
    query = "What are the rules for an LBW dismissal?"
    res = query_cricket_rules(query, k=2)
    print(f"\n[Test 2] Query: {query}")
    print(f"Top Law Retrieved: {res['sources'][0]['law_number']}")
    print(f"Top Title: {res['sources'][0]['section_title']}")

    top_text = res['sources'][0]['text'].lower()
    assert "36" in res['sources'][0]['law_number'] or "lbw" in top_text or "leg before wicket" in top_text, \
        "Expected Law 36 / LBW rule in top retrieved sources"
    
    # Visual Scenario Verification
    assert res.get("visual_scenario") is not None, "Expected a visual scenario for LBW"
    assert "lbw" in res["visual_scenario"]["file_name"].lower(), \
        f"Expected LBW visual, got: {res['visual_scenario']['file_name']}"
    print(f"Visual Explainer Matched: {res['visual_scenario']['title']} ({res['visual_scenario']['file_name']})")
    print("[PASS] Test 2: LBW rule (Law 36) and Hawkeye visual explainer successfully verified.")


def test_guardrail_unrelated_query():
    query = "What is the offside rule in football?"
    res = query_cricket_rules(query, k=2)
    print(f"\n[Test 3 - Guardrail] Query: {query}")
    print(f"Answer: {res['answer']}")
    print(f"Guardrail Triggered: {res['guardrail_triggered']}")

    assert GUARDRAIL_FALLBACK_MESSAGE.lower() in res['answer'].lower(), \
        f"Expected guardrail message '{GUARDRAIL_FALLBACK_MESSAGE}', got: {res['answer']}"
    assert res.get("visual_scenario") is None, \
        "Unrelated query must NOT attach a visual scenario"
    print("[PASS] Test 3: Guardrail successfully triggered and suppressed visual attachments.")


def test_links_inquiry():
    query = "Where can I get a Gemini API key or find official rule links?"
    res = query_cricket_rules(query, k=2)
    print(f"\n[Test 4 - Official Links] Query: {query}")
    print(f"Answer: {res['answer']}")

    assert "https://aistudio.google.com/app/apikey" in res['answer'], \
        "Expected Google AI Studio API key portal link in response"
    assert "https://www.icc-cricket.com/about/cricket/rules-and-regulations/playing-conditions" in res['answer'], \
        "Expected ICC official rules link in response"
    print("[PASS] Test 4: Official API key and rule links returned accurately.")


def test_additional_visual_scenarios():
    # Test Mankad
    q_mankad = "Can a bowler run out a non-striker leaving crease early (Mankad)?"
    res_mankad = query_cricket_rules(q_mankad, k=2)
    assert res_mankad.get("visual_scenario") is not None, "Expected visual scenario for Mankad"
    assert "mankad" in res_mankad["visual_scenario"]["file_name"].lower()
    print(f"\n[Test 5 - Visuals] Mankad Visual Matched: {res_mankad['visual_scenario']['title']}")

    # Test Powerplay
    q_powerplay = "How do powerplay and 30-yard circle fielding restrictions work?"
    res_powerplay = query_cricket_rules(q_powerplay, k=2)
    assert res_powerplay.get("visual_scenario") is not None, "Expected visual scenario for Powerplay"
    assert "powerplay" in res_powerplay["visual_scenario"]["file_name"].lower()
    print(f"[Test 5 - Visuals] Powerplay Visual Matched: {res_powerplay['visual_scenario']['title']}")
    print("[PASS] Test 5: Additional specialized visual scenarios verified.")


def test_dynamic_topic_specific_links():
    # 1. Test LBW (Law 36)
    q_lbw = "What are the rules for an LBW dismissal?"
    res_lbw = query_cricket_rules(q_lbw, k=2)
    print(f"\n[Test 6 - Dynamic Links] LBW Link: {res_lbw.get('dynamic_link')}")
    assert "leg-before-wicket" in res_lbw["answer"] or "leg-before-wicket" in str(res_lbw.get("dynamic_link")), \
        "Expected exact Lords.org LBW link for Law 36"
    assert "Read Official" in res_lbw["answer"], "Expected 'Read Official' citation format in answer"
    assert "📌" in res_lbw["answer"], "Expected pin emoji in citation"

    # 2. Test Helmet on Ground (Law 28)
    q_helmet = "What happens if the ball hits the helmet resting on the ground behind the keeper?"
    res_helmet = query_cricket_rules(q_helmet, k=2)
    print(f"[Test 6 - Dynamic Links] Helmet Link: {res_helmet.get('dynamic_link')}")
    assert "fielders-equipment" in str(res_helmet.get("dynamic_link")) or "fielders-equipment" in res_helmet["answer"] or "the-fielder" in res_helmet["answer"], \
        "Expected exact Lords.org Fielder's Equipment link for Law 28"

    # 3. Test No Ball (Law 21)
    q_noball = "What are the rules for a front-foot No Ball overstepping the popping crease?"
    res_noball = query_cricket_rules(q_noball, k=2)
    print(f"[Test 6 - Dynamic Links] No Ball Link: {res_noball.get('dynamic_link')}")
    assert "no-ball" in res_noball["answer"] or "no-ball" in str(res_noball.get("dynamic_link")), \
        "Expected exact Lords.org No Ball link for Law 21"

    # 4. Test Caught (Law 33)
    q_caught = "What constitutes a fair catch on the boundary relay?"
    res_caught = query_cricket_rules(q_caught, k=2)
    print(f"[Test 6 - Dynamic Links] Caught Link: {res_caught.get('dynamic_link')}")
    assert "caught" in res_caught["answer"] or "caught" in str(res_caught.get("dynamic_link")), \
        "Expected exact Lords.org Caught link for Law 33"

    # 5. Direct helper function mapping verification
    assert get_dynamic_rule_link("Law 36 (LBW)") == "https://www.lords.org/mcc/the-laws-of-cricket/leg-before-wicket"
    assert get_dynamic_rule_link("Law 33 (Caught)") == "https://www.lords.org/mcc/the-laws-of-cricket/caught"
    assert get_dynamic_rule_link("Law 20 (Dead Ball)") == "https://www.lords.org/mcc/the-laws-of-cricket/dead-ball"
    assert get_dynamic_rule_link("Law 21 (No Ball)") == "https://www.lords.org/mcc/the-laws-of-cricket/no-ball"
    assert get_dynamic_rule_link("Law 28 (Fielder's Equipment / Helmet)") == "https://www.lords.org/mcc/the-laws-of-cricket/fielders-equipment"
    assert get_dynamic_rule_link("Law 31 (Appeals)") == "https://www.lords.org/mcc/the-laws-of-cricket/appeals"
    assert get_dynamic_rule_link("Law 38 (Run Out)") == "https://www.lords.org/mcc/the-laws-of-cricket/run-out"
    assert get_dynamic_rule_link("Generic non-matching rule") == "https://www.lords.org/mcc/the-laws-of-cricket"

    print("[PASS] Test 6: Dynamic topic-specific law links verified successfully.")


if __name__ == "__main__":
    print("Running Cricket Rules Visual RAG verification suite...")
    test_helmet_on_ground_rule()
    test_lbw_rule()
    test_guardrail_unrelated_query()
    test_links_inquiry()
    test_additional_visual_scenarios()
    test_dynamic_topic_specific_links()
    print("\n[SUCCESS] ALL VISUAL RAG VERIFICATION TESTS PASSED SUCCESSFULLY!")
