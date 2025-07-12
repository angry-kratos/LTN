# verify_rule_consistency.py
import os
import json
from z3 import *
from tqdm import tqdm

GROUNDINGS_DIR = "data/groundings"
THRESHOLD = 0.5  # Predicate considered True if >= threshold
MAX_SCENES = 100  # Limit for testing

def is_rule_consistent(obj_id, preds):
    s = Solver()

    is_cube = Bool(f"is_cube_{obj_id}")
    is_red = Bool(f"is_red_{obj_id}")

    cube_val = preds.get("is_cube", 0.0) >= THRESHOLD
    red_val = preds.get("is_red", 0.0) >= THRESHOLD

    s.add(is_cube == cube_val)
    s.add(is_red == red_val)

    # Rule: is_red(X) ← is_cube(X) → ¬(is_cube ∧ ¬is_red) should be unsatisfiable
    s.push()
    s.add(is_cube == True, is_red == False)
    result = s.check()
    debug_msg = f"Debug: obj_id={obj_id}, is_cube={cube_val}, is_red={red_val}, result={result}"
    print(debug_msg)
    s.pop()

    return result == unsat

def verify_rule_on_scenes():
    print("\n🚀 Starting rule verification: IF is_red THEN is_cube\n")

    consistent_count = 0
    inconsistent_scenes = []

    if not os.path.exists(GROUNDINGS_DIR):
        print(f"❌ Groundings directory not found: {GROUNDINGS_DIR}")
        return

    scene_files = [f for f in os.listdir(GROUNDINGS_DIR) if f.endswith(".json")]
    if MAX_SCENES:
        scene_files = scene_files[:MAX_SCENES]
    total_files = len(scene_files)

    print(f"🧾 Found {total_files} scene files.\n")

    all_scores = []
    for idx, filename in enumerate(tqdm(scene_files, desc="🔍 Checking scenes")):
        with open(os.path.join(GROUNDINGS_DIR, filename)) as f:
            scene = json.load(f)

        for i, obj in enumerate(scene.get("objects", [])):
            obj_id = obj.get("id", f"{filename}_obj{i}")
            obj["id"] = obj_id

            preds = obj.get("predicates", {})
            if not preds:
                continue

            consistent = is_rule_consistent(obj_id, preds)
            all_scores.append(consistent)
            if consistent:
                consistent_count += 1
            else:
                inconsistent_scenes.append((filename, obj_id, preds))

    print("\n✅ Rule verification complete.")
    print(f"✅ Rule holds in {consistent_count} objects.")
    print(f"❌ Inconsistent in {len(inconsistent_scenes)} objects.")

    if inconsistent_scenes:
        print("\n⚠️ Example inconsistencies:")
        for scene, obj_id, pred in inconsistent_scenes[:5]:
            print(f"  Scene: {scene}, Object ID: {obj_id} → Predicates: {pred}")

    # Save results
    results = [{"rule": "is_red(X) ← is_cube(X)", "consistency_scores": all_scores}]
    with open("rule_verification_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("✅ Results saved to rule_verification_results.json")

if __name__ == "__main__":
    verify_rule_on_scenes()