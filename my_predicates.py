# my_predicates.py
import os
import json
import random

GROUNDINGS_DIR = "data/groundings"
PREDICATES = ["is_red", "is_cube", "is_sphere", "is_large"]

for filename in os.listdir(GROUNDINGS_DIR):
    if filename.endswith(".json"):
        path = os.path.join(GROUNDINGS_DIR, filename)
        with open(path, "r") as f:
            data = json.load(f)

        for obj in data.get("objects", []):
            is_cube = random.random() < 0.7  # 70% chance cube
            is_red = is_cube and (random.random() < 0.9)  # 90% chance red if cube
            is_sphere = not is_cube and (random.random() < 0.5)  # spheres if not cubes
            is_large = random.random() < 0.6  # 60% chance large

            obj["predicates"] = {
                "is_red": 1.0 if is_red else 0.0,
                "is_cube": 1.0 if is_cube else 0.0,
                "is_sphere": 1.0 if is_sphere else 0.0,
                "is_large": 1.0 if is_large else 0.0
            }

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

print("✅ Correlated predicate values written!")