import json

with open("rule_verification_results.json", "r") as f:
    data = json.load(f)

# Filter and sort by average consistency score (descending)
filtered = sorted(data, key=lambda x: sum(x['consistency_scores']) / len(x['consistency_scores']), reverse=True)

top_rules = filtered[:5]  # Adjust the number of top rules you want
for rule in top_rules:
    avg = sum(rule['consistency_scores']) / len(rule['consistency_scores'])
    print(f"{rule['rule']} → Avg Score: {avg:.2f}")
