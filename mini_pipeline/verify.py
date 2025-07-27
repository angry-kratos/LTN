from typing import List, Dict, Tuple


def verify_rules(rules: List[Tuple[str, float]], groundings: List[Dict]) -> List[Dict]:
    """Verify each rule across scenes."""
    results = []
    for rule, score in rules:
        head, body = rule.split(" <- ")
        body_pred = body.replace("(X)", "")
        head_pred = head.replace("(X)", "")
        consistent = True
        for scene in groundings:
            for obj in scene.get("objects", []):
                preds = obj.get("predicates", {})
                if body_pred in preds and head_pred not in preds:
                    consistent = False
                    break
            if not consistent:
                break
        results.append({"rule": rule, "satisfaction": score, "consistent": consistent})
    return results
