import json
from itertools import combinations

PREDICATES = ["is_red", "is_blue", "is_cube", "is_sphere", "is_large", "is_small"]
rules = []

# Unary rules: A(X) <- B(X)
for head, body in combinations(PREDICATES, 2):
    rules.append({"rule": f"{head}(X) <- {body}(X)"})

# Binary rules: A(X,Y) <- B(X)      &      C(Y)      &      D(X)
for (b, c, d) in combinations(PREDICATES, 3):
    rules.append({"rule": f"{b}(X,Y) <- {b}(X)      &      {c}(Y)      &      {d}(X)"})

# Save
with open("synthesized_rules.json", "w") as f:
    json.dump(rules, f, indent=2)

print(f" Generated {len(rules)} rules and saved to 'synthesized_rules.json'")
