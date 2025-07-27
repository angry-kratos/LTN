from typing import List, Dict


def validate_groundings(groundings: List[Dict]) -> bool:
    """Ensure each object has predicates for color and shape."""
    for scene in groundings:
        for obj in scene.get("objects", []):
            preds = obj.get("predicates", {})
            if not any(p.startswith("color_") for p in preds):
                print(f"Scene {scene['scene_id']} object {obj['id']} missing color")
                return False
            if not any(p.startswith("shape_") for p in preds):
                print(f"Scene {scene['scene_id']} object {obj['id']} missing shape")
                return False
    print("Validation complete")
    return True
