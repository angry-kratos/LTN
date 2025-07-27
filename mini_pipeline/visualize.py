from typing import List, Dict


def visualize_rule(rule: str, groundings: List[Dict]) -> None:
    """Print objects satisfying the rule."""
    head, body = rule.split(" <- ")
    body_pred = body.replace("(X)", "")
    head_pred = head.replace("(X)", "")
    for scene in groundings:
        matching = []
        for obj in scene.get("objects", []):
            preds = obj.get("predicates", {})
            if body_pred in preds and head_pred in preds:
                matching.append(obj["id"])
        print(f"Scene {scene['scene_id']}: Objects {matching} satisfy '{rule}'")
