import sys
from pathlib import Path

# Allow running as a script
sys.path.append(str(Path(__file__).resolve().parent))

import data
import ground
import validate
import synthesize
import verify
import analyze
import visualize
import evaluate
import summarize


def main():
    base = Path(__file__).resolve().parent
    scenes = data.load_scenes(base / "sample_scenes.json")
    groundings = ground.compute_groundings(scenes)

    print("=== Step 1: Validation ===")
    if not validate.validate_groundings(groundings):
        return

    print("\n=== Step 2: Rule Synthesis ===")
    rules = synthesize.synthesize_rules(groundings)
    for rule, score in rules:
        print(f" {rule} -> {score:.2f}")

    print("\n=== Step 3: Rule Verification ===")
    ver_results = verify.verify_rules(rules, groundings)
    for res in ver_results:
        print(f" {res['rule']} consistent={res['consistent']}")

    print("\n=== Step 4: Analysis ===")
    ranked = analyze.rank_rules(ver_results)
    for r in ranked:
        print(f" {r['rule']} score={r['satisfaction']:.2f} consistent={r['consistent']}")

    print("\n=== Step 5: Visualization ===")
    if ranked:
        visualize.visualize_rule(ranked[0]['rule'], groundings)

    print("\n=== Step 6: Evaluation ===")
    results = evaluate.evaluate(ranked)

    print("\n=== Step 7: Summary ===")
    summary = summarize.summarize(results)
    print(summary)


if __name__ == "__main__":
    main()
