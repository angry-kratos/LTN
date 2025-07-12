import json
import matplotlib.pyplot as plt

# Load rule verification results
with open("rule_verification_results.json", "r") as f:
    data = json.load(f)

# Calculate average consistency scores
rules = [
    {
        "rule": d["rule"].replace("←", "<-"),
        "avg_score": sum(d["consistency_scores"]) / len(d["consistency_scores"])
    }
    for d in data
]

# Sort rules by consistency score
rules = sorted(rules, key=lambda x: x["avg_score"], reverse=True)

# Limit number of rules in plot for readability
top_n = 10
rules = rules[:top_n]

# Plotting
plt.figure(figsize=(12, 6))
bars = plt.bar([r["rule"] for r in rules], [r["avg_score"] for r in rules])
plt.xticks(rotation=45, ha='right')
plt.ylim(0, 1)
plt.ylabel("Average Consistency Score")
plt.title("Top Rule Consistency Scores")
plt.grid(axis='y', linestyle='--', alpha=0.6)

# Annotate bars with score
for bar, r in zip(bars, rules):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, height + 0.01, f"{r['avg_score']:.2f}", 
             ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig("improved_consistency_plot.png")
plt.show()
