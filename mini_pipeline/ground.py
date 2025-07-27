from typing import Dict, List


def compute_groundings(scenes: List[Dict]) -> List[Dict]:
    """Convert scenes into simple predicate groundings."""
    groundings = []
    for scene in scenes:
        objects = scene.get("objects", [])
        scene_grounding = []
        # compute pairwise relations
        for obj in objects:
            preds = {
                f"color_{obj['color']}": True,
                f"shape_{obj['shape']}": True,
            }
            scene_grounding.append({"id": obj["id"], "predicates": preds, "position": obj["position"]})
        # add left_of relations
        for i, a in enumerate(scene_grounding):
            for b in scene_grounding[i + 1 :]:
                if a["position"][0] < b["position"][0]:
                    a.setdefault("relations", []).append({"left_of": b["id"]})
                elif a["position"][0] > b["position"][0]:
                    b.setdefault("relations", []).append({"left_of": a["id"]})
        groundings.append({"scene_id": scene["id"], "objects": scene_grounding})
    return groundings
