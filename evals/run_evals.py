import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent.graph import ticket_agent_app

def run_evaluation_suite():
    eval_file = os.path.join(os.path.dirname(__file__), "eval_dataset.json")
    with open(eval_file, "r", encoding="utf-8-sig") as f:
        test_cases = json.load(f)

    print("=" * 65)
    print("       RESOLVEAI AGENT EVALUATION BENCHMARK SUITE")
    print("=" * 65)

    passed_count = 0
    total_count = len(test_cases)

    for case in test_cases:
        case_id = case["id"]
        description = case["description"]
        ticket = case["ticket"]

        state = {
            "ticket_id": ticket["ticket_id"],
            "customer_id": ticket["customer_id"],
            "subject": ticket["subject"],
            "message": ticket["message"],
            "gathered_facts": {},
            "actions_taken": [],
            "policy_failures": [],
        }

        result = ticket_agent_app.invoke(state)

        status_ok = result.get("final_status") == case["expected_status"]
        intent_ok = result.get("intent") == case["expected_intent"]
        text_ok = case["contains_in_response"].lower() in result.get("final_reply", "").lower()

        if status_ok and intent_ok and text_ok:
            passed_count += 1
            print(f"  [PASS] {case_id}: {description}")
        else:
            print(f"  [FAIL] {case_id}: {description}")
            if not status_ok:
                print(f"         Expected status '{case['expected_status']}', got '{result.get('final_status')}'")
            if not intent_ok:
                print(f"         Expected intent '{case['expected_intent']}', got '{result.get('intent')}'")
            if not text_ok:
                print(f"         Reply did not contain '{case['contains_in_response']}'")

    print("-" * 65)
    pass_rate = (passed_count / total_count) * 100
    print(f"Total Evaluated: {total_count} | Passed: {passed_count} | Pass Rate: {pass_rate:.1f}%")
    print("=" * 65)

    if pass_rate < 100.0:
        print("[!] Evaluation gate failed: Pass rate below 100%. Blocking delivery.")
        sys.exit(1)
    else:
        print("[+] All evaluation gates passed. Safe to ship.")
        sys.exit(0)

if __name__ == "__main__":
    run_evaluation_suite()
