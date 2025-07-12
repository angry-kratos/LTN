import json
import os
from verify_rule_consistency import RuleVerifier

GROUNDINGS_DIR = "data/groundings"
RULES_FILE = "synthesized_rules_fixed.json"

def load_groundings():
    groundings = []
    for fname in os.listdir(GROUNDINGS_DIR):
        if fname.endswith(".json"):
            with open(os.path.join(GROUNDINGS_DIR, fname)) as f:
                scene = json.load(f)
                groundings.append((fname, scene))
    return groundings

if __name__ == "__main__":
    with open(RULES_FILE) as f:
        rules = json.load(f)
        print("Loaded rules type:", type(rules))
        print("First rule example:", rules[0])
        rule_strings = [r[0] for r in rules] 



    verifier = RuleVerifier(predicates=[
        "is_red", "is_cube", "is_sphere", "is_cylinder",
        "is_small", "is_large", "is_metal", "is_rubber"
    ])

    groundings = load_groundings()

    for rule in rule_strings:
        consistent_count = 0
        total = 0
        for fname, scene in groundings[:100]:  # limit to 100 for speed
            consistent, counterex = verifier.verify_rule(rule, scene)
            total += 1
            if consistent:
                consistent_count += 1
        print(f"Rule: {rule}")
        print(f"  Consistent in {consistent_count}/{total} scenes\n")
