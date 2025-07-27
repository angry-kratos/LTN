from typing import Dict


def summarize(results: Dict) -> str:
    """Return a markdown summary."""
    best_rule = results.get("best_rule")
    summary = ["# Pipeline Summary", ""]
    summary.append(f"Total rules: {results['total_rules']}")
    if best_rule:
        summary.append(f"Best rule: {best_rule['rule']} (score={best_rule['satisfaction']:.2f}, consistent={best_rule['consistent']})")
    return "\n".join(summary)
