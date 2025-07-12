
from verify_rule_consistency import verify_rules


if __name__ == "__main__":
    print("🚀 Starting rule verification ...")  # Add this line
    verify_rules(
        rules_file="synthesized_rules.json",
        groundings_dir="data/groundings",
        output_file="rule_verification_results.json"
    )
    print(" Rule verification finished!")      # And this line
