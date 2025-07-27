from typing import List, Dict, Tuple


def synthesize_rules(groundings: List[Dict]) -> List[Tuple[str, float]]:
    """Generate simple rules and compute satisfaction."""
    candidates = [
        ("color_red(X) <- shape_cube(X)", 0.0),
        ("color_blue(X) <- shape_sphere(X)", 0.0),
    ]
    for rule_idx, (rule, _) in enumerate(candidates):
        head, body = rule.split(" <- ")
        body_pred = body.replace("(X)", "")
        head_pred = head.replace("(X)", "")
        total = 0
        satisfied = 0
        for scene in groundings:
            for obj in scene.get("objects", []):
                preds = obj.get("predicates", {})
                if body_pred in preds:
                    total += 1
                    if head_pred in preds:
                        satisfied += 1
        score = satisfied / total if total else 0.0
        candidates[rule_idx] = (rule, score)
    return candidates
