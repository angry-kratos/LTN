from typing import List, Dict


def evaluate(ranked_rules: List[Dict]) -> Dict:
    """Return simple metrics for the rules."""
    best = ranked_rules[0] if ranked_rules else None
    return {
        "total_rules": len(ranked_rules),
        "best_rule": best,
    }
