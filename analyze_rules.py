import json
import pandas as pd
from typing import List, Dict, Any
import matplotlib.pyplot as plt
import seaborn as sns
import os

def load_results(rules_file: str, verification_file: str) -> List[Dict]:
    """Load synthesized rules and their verification results"""
    with open(rules_file, "r") as f:
        rules = json.load(f)
    
    with open(verification_file, "r") as f:
        verification_results = json.load(f)
    
    # Combine results
    results = []
    for rule, verification in zip(rules, verification_results):
        result = {
            "rule": verification["rule"],
            "satisfaction_score": rule[1],
            "consistency_score": verification["overall_consistency"],
            "counterexamples": len(verification["counterexamples"]),
            "num_scenes": len(verification["consistency_scores"]),
            "is_consistent": verification["overall_consistency"] == 1.0
        }
        results.append(result)
    
    return results

def rank_rules(results: List[Dict]) -> List[Dict]:
    """Rank rules based on combined satisfaction and consistency scores"""
    # Calculate combined score (weighted average)
    for result in results:
        # Weight satisfaction and consistency equally
        combined_score = (result["satisfaction_score"] + result["consistency_score"]) / 2
        result["combined_score"] = combined_score
    
    # Sort by combined score
    results.sort(key=lambda x: x["combined_score"], reverse=True)
    return results

def export_results(results: List[Dict], output_dir: str):
    """Export results to CSV and JSON"""
    # Create DataFrame
    df = pd.DataFrame(results)
    
    # Export to CSV
    csv_path = os.path.join(output_dir, "rule_analysis.csv")
    df.to_csv(csv_path, index=False)
    
    # Export to JSON
    json_path = os.path.join(output_dir, "rule_analysis.json")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    
    return df

def visualize_results(df: pd.DataFrame, output_dir: str):
    """Create visualizations of rule performance"""
    # Create plots directory if it doesn't exist
    plots_dir = os.path.join(output_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)
    
    # Distribution of scores
    plt.figure(figsize=(12, 6))
    sns.histplot(data=df, x="combined_score", bins=20)
    plt.title("Distribution of Combined Rule Scores")
    plt.xlabel("Combined Score")
    plt.ylabel("Number of Rules")
    plt.savefig(os.path.join(plots_dir, "score_distribution.png"))
    plt.close()
    
    # Satisfaction vs Consistency
    plt.figure(figsize=(12, 6))
    sns.scatterplot(data=df, x="satisfaction_score", y="consistency_score")
    plt.title("Satisfaction vs Consistency Scores")
    plt.xlabel("Satisfaction Score")
    plt.ylabel("Consistency Score")
    plt.savefig(os.path.join(plots_dir, "score_comparison.png"))
    plt.close()
    
    # Top 10 rules
    top_10 = df.nlargest(10, "combined_score")
    plt.figure(figsize=(12, 6))
    sns.barplot(data=top_10, x="combined_score", y="rule")
    plt.title("Top 10 Rules by Combined Score")
    plt.xlabel("Combined Score")
    plt.ylabel("Rule")
    plt.savefig(os.path.join(plots_dir, "top_rules.png"))
    plt.close()

def analyze_rules(rules_file: str, verification_file: str, output_dir: str):
    """Main analysis function"""
    # Load results
    results = load_results(rules_file, verification_file)
    
    # Rank rules
    ranked_results = rank_rules(results)
    
    # Export results
    df = export_results(ranked_results, output_dir)
    
    # Visualize results
    visualize_results(df, output_dir)
    
    # Print summary statistics
    print("\n=== Rule Analysis Summary ===")
    print(f"Total rules analyzed: {len(ranked_results)}")
    print(f"Rules with perfect consistency: {df[df['is_consistent']].shape[0]}")
    print(f"Average combined score: {df['combined_score'].mean():.3f}")
    print(f"Top rule score: {df['combined_score'].max():.3f}")
    print("\nTop 5 rules:")
    for i, row in df.head(5).iterrows():
        print(f"\nRule {i+1}:")
        print(f"Rule: {row['rule']}")
        print(f"Combined Score: {row['combined_score']:.3f}")
        print(f"Satisfaction: {row['satisfaction_score']:.3f}")
        print(f"Consistency: {row['consistency_score']:.3f}")
        print(f"Counterexamples: {row['counterexamples']}")

if __name__ == "__main__":
    analyze_rules(
        rules_file="synthesized_rules.json",
        verification_file="rule_verification_results.json",
        output_dir="results"
    )
