import os
import json

GROUNDINGS_DIR = "data/groundings"

def inspect_structure():
    files = [f for f in os.listdir(GROUNDINGS_DIR) if f.endswith(".json")]
    
    print(f"Found {len(files)} JSON files in {GROUNDINGS_DIR}")
    
    sample_file = os.path.join(GROUNDINGS_DIR, files[0])
    print(f"Inspecting file: {sample_file}")
    
    with open(sample_file, 'r') as f:
        scene = json.load(f)

    print(f"Top-level keys in scene file: {list(scene.keys())}")
    
    for i, obj in enumerate(scene.get("objects", [])):
        print(f"Object {i+1}:")
        print(f"  Name: {obj.get('name')}")
        print(f"  Predicates: {obj.get('predicates', {})}")
        if i == 2:
            break  # Only show the first 3 objects for clarity

if __name__ == "__main__":
    inspect_structure()

