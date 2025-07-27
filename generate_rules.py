import json

predicates = ["is_red", "is_blue", "is_cube", "is_sphere", "is_large"]

rules = [
    {"rule": f"{predicates[0]}(X) <- {predicates[2]}(X)"},
    {"rule": f"{predicates[1]}(X,Y) <- {predicates[2]}(X) & {predicates[3]}(Y) & {predicates[4]}(X)"}
]

with open("synthesized_rules.json", "w") as f:
    json.dump(rules, f, indent=2)
