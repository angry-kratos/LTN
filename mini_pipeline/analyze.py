from typing import List, Dict


def rank_rules(results: List[Dict]) -> List[Dict]:
    """Rank rules by satisfaction and consistency."""
    ranked = sorted(
        results,
        key=lambda r: (r["consistent"], r["satisfaction"]),
        reverse=True,
    )
    return ranked
