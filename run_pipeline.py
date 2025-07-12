#!/usr/bin/env python3

import os
import subprocess
import sys
import time
import json
from pathlib import Path

def get_project_root() -> Path:
    """Get the absolute path to the project root"""
    return Path(__file__).parent.absolute()

def run_command(command: str, cwd: str = None) -> None:
    """Run a command and print its output"""
    print(f"\n=== Running: {command} ===")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd
        )
        print(result.stdout)
        if result.stderr:
            print(f"\n=== Error Output ===")
            print(result.stderr)
        if result.returncode != 0:
            print(f"\n=== Command Failed ===")
            print(f"Exit code: {result.returncode}")
            sys.exit(1)
    except Exception as e:
        print(f"\n=== Exception ===")
        print(str(e))
        sys.exit(1)

def create_directories(root: Path) -> None:
    """Create necessary directories"""
    dirs = [
        root / "results",
        root / "visualizations",
        root / "evaluation_results"
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(exist_ok=True)

def main():
    """Run the complete pipeline"""
    print("Starting Neural-Symbolic Visual Reasoning Pipeline...")
    root = get_project_root()
    
    # Create necessary directories
    create_directories(root)
    
    # 1. Data Validation
    print("\n=== Step 1: Data Validation ===")
    run_command("python3 validate_groundings.py", cwd=str(root))
    
    # 2. Rule Synthesis
    print("\n=== Step 2: Rule Synthesis ===")
    run_command("python3 synthesize_rules.py", cwd=str(root))
    
    # 3. Rule Verification
    print("\n=== Step 3: Rule Verification ===")
    run_command("python3 verify_rule_consistency.py", cwd=str(root))
    
    # 4. Rule Analysis
    print("\n=== Step 4: Rule Analysis ===")
    run_command("python3 analyze_rules.py", cwd=str(root))
    
    # 5. Visualization
    print("\n=== Step 5: Visualization ===")
    run_command("python3 visualize_rules.py", cwd=str(root))
    
    # 6. Evaluation
    print("\n=== Step 6: Evaluation ===")
    run_command("python3 evaluate_rules.py", cwd=str(root))
    
    # 7. Results Summary
    print("\n=== Step 7: Results Summary ===")
    run_command("python3 summarize_results.py", cwd=str(root))
    
    print("\n=== Pipeline Complete ===")
    print("Results are available in the following directories:")
    print(f"- {root / 'results'}")
    print(f"- {root / 'visualizations'}")
    print(f"- {root / 'evaluation_results'}")
    print(f"- {root / 'results_summary.md'}")

if __name__ == "__main__":
    main()
