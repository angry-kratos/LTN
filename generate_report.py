import json

with open("rule_verification_results.json", "r") as f:
    data = json.load(f)

summary_lines = [
    "# 🧠 Rule Consistency Report\n",
    "| Rule | Avg. Consistency |",
    "|------|------------------|"
]

for rule in data:
    scores = rule["consistency_scores"]
    if scores:
        avg = sum(scores) / len(scores)
        summary_lines.append(f"| `{rule['rule']}` | `{avg:.2f}` |")

with open("consistency_report.md", "w") as f:
    f.write("\n".join(summary_lines))

print(" Markdown report generated as 'consistency_report.md'")
