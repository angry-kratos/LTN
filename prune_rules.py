import json

with open("rule_verification_results.json", "r") as f:
    data = json.load(f)

THRESHOLD = 0.5
filtered_rules = []

for rule in data:
    scores = rule.get("consistency_scores", [])
    if scores:
        avg_score = sum(scores) / len(scores)
        if avg_score >= THRESHOLD:
            filtered_rules.append(rule)

# Save pruned rules
with open("pruned_rules.json", "w") as f:
    json.dump(filtered_rules, f, indent=2)

print(f" Pruned and saved {len(filtered_rules)} high-consistency rules to 'pruned_rules.json'")
