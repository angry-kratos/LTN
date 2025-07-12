import json, os

GROUNDINGS_DIR = "data/groundings"
EXPECTED_PREDICATES = 15  # set to 8 if that's the expected number

error_count = 0

for filename in os.listdir(GROUNDINGS_DIR):
    if filename.endswith(".json"):
        path = os.path.join(GROUNDINGS_DIR, filename)
        with open(path, "r") as f:
            scene = json.load(f)
        
        for obj in scene.get("objects", []):
            preds = obj.get("predicates", {})
            if len(preds) != EXPECTED_PREDICATES:
                print(f" Error in {filename} — object {obj.get('id', 'UNKNOWN')}: Expected {EXPECTED_PREDICATES} predicates, found {len(preds)}")
                error_count += 1

print(f"\n Validation complete. Found {error_count} errors.")
