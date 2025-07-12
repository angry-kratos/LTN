import json
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
from typing import List, Dict, Any

class RuleVisualizer:
    def __init__(self, clevr_dir: str):
        self.clevr_dir = clevr_dir
        self.font = ImageFont.load_default()
        
    def _load_image(self, scene_id: str) -> Image.Image:
        """Load CLEVR image for a given scene"""
        image_path = os.path.join(
            self.clevr_dir,
            "images",
            "val",
            f"CLEVR_val_{scene_id}.png"
        )
        return Image.open(image_path)
    
    def _draw_bounding_boxes(self, img: Image.Image, scene: Dict, color: str = "red") -> Image.Image:
        """Draw bounding boxes around objects in the scene"""
        draw = ImageDraw.Draw(img)
        
        for obj in scene["objects"]:
            x, y, w, h = obj["bbox"]
            draw.rectangle(
                [(x, y), (x + w, y + h)],
                outline=color,
                width=3
            )
            
            # Add object ID
            draw.text(
                (x + 5, y + 5),
                str(obj["id"]),
                fill=color,
                font=self.font
            )
        
        return img
    
    def _highlight_satisfied_objects(self, img: Image.Image, scene: Dict, rule: str) -> Image.Image:
        """Highlight objects that satisfy the rule"""
        draw = ImageDraw.Draw(img)
        
        # Parse rule to identify relevant objects
        head, body = rule.split("←")
        head = head.strip()
        body = body.strip()
        
        # Get object IDs that satisfy the rule
        satisfied_ids = self._get_satisfied_objects(scene, rule)
        
        # Highlight satisfied objects with green boxes
        for obj in scene["objects"]:
            if obj["id"] in satisfied_ids:
                x, y, w, h = obj["bbox"]
                draw.rectangle(
                    [(x, y), (x + w, y + h)],
                    outline="green",
                    width=5
                )
                
                # Add rule text
                text_y = y + h + 10
                draw.text(
                    (x + 5, text_y),
                    head,
                    fill="green",
                    font=self.font
                )
        
        return img
    
    def _get_satisfied_objects(self, scene: Dict, rule: str) -> List[str]:
        """Determine which objects satisfy the rule"""
        satisfied_ids = []
        
        # Parse rule to identify relevant objects
        head, body = rule.split("←")
        head = head.strip()
        body = body.strip()
        
        # Get predicate names from rule
        predicates = set()
        for part in [head] + body.split("∧"):
            pred_name, _ = part.split("(")
            predicates.add(pred_name.strip())
        
        # Check each object
        for obj in scene["objects"]:
            satisfies = True
            for pred in predicates:
                if pred in obj["predicates"]:
                    if obj["predicates"][pred] < 0.5:  # threshold for satisfaction
                        satisfies = False
                        break
            
            if satisfies:
                satisfied_ids.append(obj["id"])
        
        return satisfied_ids
    
    def visualize_rule(self, scene_id: str, rule: str, scene: Dict, output_dir: str):
        """Create visualization of rule satisfaction for a scene"""
        # Load and process image
        img = self._load_image(scene_id)
        img = self._draw_bounding_boxes(img, scene)
        img = self._highlight_satisfied_objects(img, scene, rule)
        
        # Save visualization
        output_path = os.path.join(
            output_dir,
            f"scene_{scene_id}_rule_{rule.replace(' ', '_')}.png"
        )
        img.save(output_path)
        
        return output_path

def create_visualizations(rules_file: str, verification_file: str, clevr_dir: str, output_dir: str):
    """Create visualizations for top rules and their counterexamples"""
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Load results
    with open(rules_file, "r") as f:
        rules = json.load(f)
    
    with open(verification_file, "r") as f:
        verification_results = json.load(f)
    
    # Initialize visualizer
    visualizer = RuleVisualizer(clevr_dir)
    
    # Process top 5 rules
    print("\n=== Creating visualizations for top rules ===")
    for i, (rule, _) in enumerate(rules[:5]):
        print(f"\nProcessing rule {i+1}: {rule}")
        
        # Find a scene that satisfies this rule
        for scene in verification_results[0]["scenes"]:
            if scene["is_consistent"]:
                scene_id = scene["id"]
                break
        
        # Create visualization
        output_path = visualizer.visualize_rule(
            scene_id=scene_id,
            rule=rule,
            scene=scene["scene"],
            output_dir=os.path.join(output_dir, "satisfied")
        )
        print(f"Visualization saved to: {output_path}")
    
    # Process counterexamples for rules with failures
    print("\n=== Creating visualizations for counterexamples ===")
    for result in verification_results:
        if result["counterexamples"]:
            # Take first counterexample
            counterexample = result["counterexamples"][0]
            scene_id = counterexample["id"]
            
            # Create visualization
            output_path = visualizer.visualize_rule(
                scene_id=scene_id,
                rule=result["rule"],
                scene=counterexample["scene"],
                output_dir=os.path.join(output_dir, "counterexamples")
            )
            print(f"Counterexample visualization saved to: {output_path}")

if __name__ == "__main__":
    create_visualizations(
        rules_file="synthesized_rules.json",
        verification_file="rule_verification_results.json",
        clevr_dir="/Users/kargichauhan/Documents/Work/LTN/CLEVR_v1.0",
        output_dir="visualizations"
    )
