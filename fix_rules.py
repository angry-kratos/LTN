import json

# Define the mapping from dummy predicates to actual grounded ones
mapping = {
    "head": "is_cube",
    "body1": "is_red",
    "body2": "is_large",
    "body3": "is_right_of"
}

# Load the original synthesized rules
with open("synthesized_rules.json", "r") as f:
    rules = json.load(f)

# Apply replacements
updated_rules = []
for rule_entry in rules:
    rule_str, score = rule_entry
    for dummy, real in mapping.items():
        rule_str = rule_str.replace(dummy, real)
    updated_rules.append([rule_str, score])

# Save to new file
with open("synthesized_rules_fixed.json", "w") as f:
    json.dump(updated_rules, f, indent=2)

print("✅ Fixed rules saved to synthesized_rules_fixed.json")

