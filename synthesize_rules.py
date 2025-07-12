import json
import z3
import numpy as np
from typing import List, Dict, Tuple
import os

class RuleSynthesizer:
    def __init__(self, predicates: List[str], max_vars: int = 3):
        self.predicates = predicates
        self.max_vars = max_vars
        self.rule_templates = self._generate_rule_templates()
        
    def _generate_rule_templates(self) -> List[str]:
        """Generate basic rule templates"""
        templates = []
        
        # Unary rules
        templates.append("head(X) ← body1(X)")
        
        # Binary spatial relations
        templates.append("head(X,Y) ← body1(X) ∧ body2(Y) ∧ body3(X,Y)")
        
        # Ternary relations
        templates.append("head(X,Y) ← body1(X,Z) ∧ body2(Z,Y) ∧ body3(X,Y)")
        
        return templates
    
    def _encode_rule(self, template: str, predicates: List[str]) -> z3.ExprRef:
        """Convert a rule template into a Z3 expression"""
        # Create variables
        vars = {f"{chr(88 + i)}": z3.Int(f"{chr(88 + i)}") for i in range(self.max_vars)}  # Use uppercase letters X, Y, Z
        
        # Split template into head and body
        head, body = template.split("←")
        head = head.strip()
        body = body.strip()
        
        # Create Z3 expressions for each predicate
        body_exprs = []
        for pred in body.split("∧"):
            pred = pred.strip()
            pred_name, var_names = pred.split("(")
            var_names = var_names.strip("()")
            var_names = var_names.split(",")
            
            # Create Z3 variables
            z3_vars = [vars[var.strip()] for var in var_names]
            
            # Create predicate expression
            pred_expr = z3.Bool(f"{pred_name}({','.join(map(str, z3_vars))})")
            body_exprs.append(pred_expr)
        
        # Combine body expressions with AND
        body_expr = z3.And(*body_exprs)
        
        # Create head expression
        head_name, var_names = head.split("(")
        var_names = var_names.strip("()")
        var_names = var_names.split(",")
        z3_vars = [vars[var.strip()] for var in var_names]
        head_expr = z3.Bool(f"{head_name}({','.join(map(str, z3_vars))})")
        
        return z3.Implies(body_expr, head_expr)
    
    def synthesize_rules(self, groundings: List[Dict]) -> List[Tuple[str, float]]:
        """
        Synthesize rules from grounded scenes
        Returns a list of (rule, satisfaction_score) tuples
        """
        rules = []
        total_scenes = len(groundings)
        
        print(f"Starting rule synthesis with {total_scenes} scenes...")
        
        for template_idx, template in enumerate(self.rule_templates):
            print(f"\nProcessing template {template_idx + 1}/{len(self.rule_templates)}: {template}")
            
            # Create Z3 solver
            solver = z3.Solver()  
            
            # Dictionary to store Z3 variables
            scene_vars = {}
            
            # Add grounded facts to solver
            for scene_idx, scene in enumerate(groundings):
                if scene_idx % 10 == 0:  
                    print(f"  Processing scene {scene_idx + 1}/{total_scenes}")
                
                for idx, obj in enumerate(scene["objects"]):
                    for pred, score in obj["predicates"].items():
                        obj_id = obj.get('id', f'obj_{idx}')
                        var_name = f"{pred}_{obj_id}"
                        if var_name not in scene_vars:
                            scene_vars[var_name] = z3.Real(var_name)
                        var = scene_vars[var_name]
                        solver.add(var >= score)
                        solver.add(var <= 1.0)
            
            # Add rule template constraint
            rule_expr = self._encode_rule(template, self.predicates)
            solver.add(rule_expr)
            
            # Check if rule is satisfiable
            if solver.check() == z3.sat:
                model = solver.model()
                satisfaction_score = self._compute_satisfaction_score(model, groundings, scene_vars)
                rules.append((template, satisfaction_score))
                print(f"  Found satisfiable rule with score: {satisfaction_score:.2f}")
            else:
                print("  Rule not satisfiable")
            
            # Clear solver to free memory
            solver.reset()
        
        # Sort rules by satisfaction score
        rules.sort(key=lambda x: x[1], reverse=True)
        
        print("\nRule synthesis complete!")
        print(f"Found {len(rules)} satisfiable rules")
        
        return rules
    
    def _compute_satisfaction_score(self, model: z3.ModelRef, groundings: List[Dict], scene_vars: Dict[str, z3.ExprRef]) -> float:
        """Compute rule satisfaction score across all scenes"""
        total_score = 0
        num_scenes = len(groundings)
        
        for scene in groundings:
            scene_score = 0
            for obj in scene["objects"]:
                for pred, score in obj["predicates"].items():
                    obj_id = obj.get('id', f'obj_{scene["objects"].index(obj)}')
                    var_name = f"{pred}_{obj_id}"
                    if var_name in scene_vars:
                        var = scene_vars[var_name]
                        # Use model.eval() to get the concrete value
                        var_value = model.eval(var)
                        # Check if the boolean value is True
                        if var_value == z3.BoolVal(True):
                            scene_score += float(var_value.as_decimal(2))
            total_score += scene_score
        
        return total_score / (num_scenes * len(self.predicates))

def load_groundings(grounding_dir: str) -> List[Dict]:
    """Load grounded scenes from JSON files"""
    groundings = []
    for filename in os.listdir(grounding_dir):
        if filename.endswith(".json"):
            with open(os.path.join(grounding_dir, filename), "r") as f:
                scene = json.load(f)
                groundings.append(scene)
    return groundings

if __name__ == "__main__":
    # Example predicates for CLEVR
    PREDICATES = [
        "is_red", "is_blue", "is_green", "is_cube", 
        "is_cylinder", "is_sphere", "is_large", "is_small"
    ]
    
    # Load groundings
    groundings = load_groundings("data/groundings")
    
    # Initialize synthesizer
    synthesizer = RuleSynthesizer(PREDICATES)
    
    # Synthesize rules
    rules = synthesizer.synthesize_rules(groundings)
    
    # Save results
    with open("synthesized_rules.json", "w") as f:
        json.dump(rules, f, indent=2)