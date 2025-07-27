import json
import numpy as np
from typing import List, Dict, Any
import random
import os
from copy import deepcopy

class RuleEvaluator:
    def __init__(self, predicates: List[str], clevr_dir: str):
        self.predicates = predicates
        self.clevr_dir = clevr_dir
        self.scenes = self._load_scenes()
        
    def _load_scenes(self) -> Dict[str, Dict]:
        """Load and organize CLEVR scenes"""
        scenes = {}
        scenes_dir = os.path.join(self.clevr_dir, "scenes")
        
        # Load validation scenes
        with open(os.path.join(scenes_dir, "CLEVR_val_scenes.json"), "r") as f:
            val_data = json.load(f)
            for scene in val_data["scenes"]:
                scenes[scene["image_filename"]] = scene
        
        return scenes
    
    def evaluate_interpretability(self, rules: List[str], num_samples: int = 10) -> Dict:
        """Evaluate rule interpretability by human inspection"""
        results = []
        
        # Randomly sample scenes for each rule
        for rule in rules:
            rule_results = {
                "rule": rule,
                "interpretability_score": 0,
                "comments": [],
                "examples": []
            }
            
            # Sample scenes where rule is satisfied
            satisfied_scenes = []
            for _ in range(num_samples):
                scene_id = random.choice(list(self.scenes.keys()))
                scene = self.scenes[scene_id]
                if self._check_rule_satisfaction(rule, scene):
                    satisfied_scenes.append(scene)
            
            # Store examples
            for scene in satisfied_scenes:
                example = {
                    "scene_id": scene["image_filename"],
                    "objects": [obj["color"] + " " + obj["shape"] for obj in scene["objects"]],
                    "relationships": scene["relationships"]
                }
                rule_results["examples"].append(example)
            
            results.append(rule_results)
        
        return results
    
    def evaluate_robustness(self, rules: List[str], perturbation_levels: List[float] = [0.1, 0.2, 0.3]) -> Dict:
        """Evaluate rule robustness to scene perturbations"""
        results = []
        
        for rule in rules:
            rule_results = {
                "rule": rule,
                "original_satisfaction": 0,
                "perturbed_satisfaction": {}
            }
            
            # Find a scene that satisfies the rule
            for scene_id, scene in self.scenes.items():
                if self._check_rule_satisfaction(rule, scene):
                    original_scene = scene
                    break
            
            # Store original satisfaction
            rule_results["original_satisfaction"] = self._check_rule_satisfaction(rule, original_scene)
            
            # Test each perturbation level
            for level in perturbation_levels:
                perturbed_scene = self._perturb_scene(original_scene, level)
                satisfaction = self._check_rule_satisfaction(rule, perturbed_scene)
                rule_results["perturbed_satisfaction"][level] = satisfaction
            
            results.append(rule_results)
        
        return results
    
    def evaluate_generalization(self, rules: List[str], test_split: float = 0.2) -> Dict:
        """Evaluate rule generalization to unseen scenes"""
        results = []
        
        # Split scenes into train/test
        scene_ids = list(self.scenes.keys())
        random.shuffle(scene_ids)
        split_idx = int(len(scene_ids) * (1 - test_split))
        train_scenes = scene_ids[:split_idx]
        test_scenes = scene_ids[split_idx:]
        
        for rule in rules:
            rule_results = {
                "rule": rule,
                "train_satisfaction": 0,
                "test_satisfaction": 0
            }
            
            # Calculate satisfaction on train set
            train_satisfaction = []
            for scene_id in train_scenes:
                train_satisfaction.append(self._check_rule_satisfaction(rule, self.scenes[scene_id]))
            rule_results["train_satisfaction"] = np.mean(train_satisfaction)
            
            # Calculate satisfaction on test set
            test_satisfaction = []
            for scene_id in test_scenes:
                test_satisfaction.append(self._check_rule_satisfaction(rule, self.scenes[scene_id]))
            rule_results["test_satisfaction"] = np.mean(test_satisfaction)
            
            results.append(rule_results)
        
        return results
    
    def evaluate_baseline(self, rules: List[str], num_random_rules: int = 10) -> Dict:
        """Compare against random rules"""
        results = []
        
        # Generate random rules
        random_rules = self._generate_random_rules(num_random_rules)
        
        for rule in rules:
            rule_results = {
                "rule": rule,
                "performance": 0,
                "random_rule_performance": []
            }
            
            # Calculate performance
            performance = []
            for scene in self.scenes.values():
                performance.append(self._check_rule_satisfaction(rule, scene))
            rule_results["performance"] = np.mean(performance)
            
            # Calculate random rule performance
            for random_rule in random_rules:
                random_performance = []
                for scene in self.scenes.values():
                    random_performance.append(self._check_rule_satisfaction(random_rule, scene))
                rule_results["random_rule_performance"].append(np.mean(random_performance))
            
            results.append(rule_results)
        
        return results
    
    def _perturb_scene(self, scene: Dict, level: float) -> Dict:
        """Perturb scene attributes by given level"""
        perturbed_scene = deepcopy(scene)
        
        for obj in perturbed_scene["objects"]:
            # Perturb position
            obj["3d_coords"] = [
                coord + random.uniform(-level, level) for coord in obj["3d_coords"]
            ]
            
            # Perturb size
            obj["size"] = obj["size"] * (1 + random.uniform(-level, level))
            
        return perturbed_scene
    
    def _generate_random_rules(self, num_rules: int) -> List[str]:
        """Generate random rules for baseline comparison"""
        random_rules = []
        
        for _ in range(num_rules):
            # Randomly select predicates
            head_pred = random.choice(self.predicates)
            body_preds = random.sample(self.predicates, random.randint(1, 3))
            
            # Create rule
            head = f"{head_pred}(X)"
            body = " ∧ ".join([f"{pred}(X)" for pred in body_preds])
            rule = f"{head} ← {body}"
            random_rules.append(rule)
        
        return random_rules
    
    def _check_rule_satisfaction(self, rule: str, scene: Dict) -> float:
        """Check if a rule is satisfied in a scene"""
        head, body = rule.split("←")
        head = head.strip()
        body = body.strip()
        
        # Get predicate names
        predicates = set()
        for part in [head] + body.split("∧"):
            pred_name, _ = part.split("(")
            predicates.add(pred_name.strip())
        
        # Check each object
        for obj in scene["objects"]:
            satisfies = True
            for pred in predicates:
                if pred in obj:
                    if obj[pred] < 0.5:  # threshold for satisfaction
                        satisfies = False
                        break
            
            if satisfies:
                return 1.0
        
        return 0.0

def evaluate_rules(rules_file: str, clevr_dir: str, output_dir: str):
    """Main evaluation function"""
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Load predicates
    PREDICATES = [
        "is_red", "is_blue", "is_green", "is_cube", 
        "is_cylinder", "is_sphere", "is_large", "is_small"
    ]
    
    # Initialize evaluator
    evaluator = RuleEvaluator(PREDICATES, clevr_dir)
    
    # Load rules
    with open(rules_file, "r") as f:
        rules = [rule["rule"] for rule in json.load(f)]
    
    # Evaluate interpretability
    print("\n=== Evaluating Interpretability ===")
    interpretability = evaluator.evaluate_interpretability(rules[:5])
    with open(os.path.join(output_dir, "interpretability_results.json"), "w") as f:
        json.dump(interpretability, f, indent=2)
    
    # Evaluate robustness
    print("\n=== Evaluating Robustness ===")
    robustness = evaluator.evaluate_robustness(rules[:5])
    with open(os.path.join(output_dir, "robustness_results.json"), "w") as f:
        json.dump(robustness, f, indent=2)
    
    # Evaluate generalization
    print("\n=== Evaluating Generalization ===")
    generalization = evaluator.evaluate_generalization(rules[:5])
    with open(os.path.join(output_dir, "generalization_results.json"), "w") as f:
        json.dump(generalization, f, indent=2)
    
    # Evaluate baseline
    print("\n=== Evaluating Baseline ===")
    baseline = evaluator.evaluate_baseline(rules[:5])
    with open(os.path.join(output_dir, "baseline_results.json"), "w") as f:
        json.dump(baseline, f, indent=2)
    
    print("\n=== Evaluation Summary ===")
    print(f"Results saved to: {output_dir}")
    print("\nTop 5 rules analysis:")
    for i, rule in enumerate(rules[:5]):
        print(f"\nRule {i+1}: {rule}")
        print("- Interpretability: ")
        print("- Robustness: ")
        print("- Generalization: ")
        print("- Baseline comparison: ")

if __name__ == "__main__":
    clevr_dir = os.getenv("CLEVR_DIR", "CLEVR_v1.0")
    evaluate_rules(
        rules_file="rule_analysis.json",
        clevr_dir=clevr_dir,
        output_dir="evaluation_results"
    )
