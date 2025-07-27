import os
import sys
import torch
import json

# Add root directory (LTN/) to Python path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)

# ─── Import predicate network definitions ────────────────────────────────────
from models.color_net import ColorNet
from models.size_net import SizeNet
from models.material_net import MaterialNet
from models.shape_net import ShapeNet

# ─── Import CLEVR data loading utilities ────────────────────────────────────
from data_utils_clevr import load_clevr_scenes, extract_object_data_for_scene

# ─── Configuration ──────────────────────────────────────────────────────────
MODEL_DIR = "models/"
# Allow overriding the CLEVR dataset path via the CLEVR_DIR environment
# variable. This makes the script portable across operating systems.
CLEVR_DIR = os.getenv("CLEVR_DIR", "CLEVR_v1.0")
SCENES_JSON = os.path.join(CLEVR_DIR, "scenes", "CLEVR_val_scenes.json")
OUT_DIR = "data/groundings/"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ─── Load trained predicate networks ────────────────────────────────────────
# ─── Load trained predicate networks ────────────────────────────────────────

#  Load full ColorNet model object
color_net = ColorNet().to(device)
color_net.load_state_dict(torch.load(os.path.join(MODEL_DIR, "color_net.pt")))
color_net.eval()


# Load other models as state_dicts
shape_net = ShapeNet().to(device)
shape_net.load_state_dict(torch.load(os.path.join(MODEL_DIR, "shape_net.pt")))
shape_net.eval()

size_net = SizeNet().to(device)
size_net.load_state_dict(torch.load(os.path.join(MODEL_DIR, "size_net.pt")))
size_net.eval()

material_net = MaterialNet().to(device)
material_net.load_state_dict(torch.load(os.path.join(MODEL_DIR, "material_net.pt")))
material_net.eval()


# ─── Build reverse lookup maps for labels ───────────────────────────────────
idx2color = {v: k for k, v in color_net.color2idx.items()}
idx2shape = {v: k for k, v in shape_net.shape2idx.items()}
idx2size  = {v: k for k, v in size_net.size2idx.items()}
idx2mat   = {v: k for k, v in material_net.mat2idx.items()}

# ─── Load CLEVR scenes ──────────────────────────────────────────────────────
all_scenes = load_clevr_scenes(SCENES_JSON)

# ─── Export groundings for each scene ───────────────────────────────────────
for scene_idx, scene in enumerate(all_scenes):
    obj_data = extract_object_data_for_scene(scene)
    scene_objects = []

    for obj_idx, (feat_tensor, _) in enumerate(obj_data):
        x = feat_tensor.unsqueeze(0).to(device)  # Shape: [1, 3]

        with torch.no_grad():
            p_color = color_net(x)[0].cpu().tolist()
            p_shape = shape_net(x)[0].cpu().tolist()
            p_size  = size_net(x)[0].cpu().tolist()
            p_mat   = material_net(x)[0].cpu().tolist()

        # Build flat predicate dictionary (15 predicates total)
        predicates = {}

        # Add color predicates: is_red, is_blue, ...
        for idx, prob in enumerate(p_color):
            color_name = idx2color[idx]
            predicates[f"is_{color_name}"] = prob

        # Add shape predicates: is_cube, is_sphere, ...
        for idx, prob in enumerate(p_shape):
            shape_name = idx2shape[idx]
            predicates[f"is_{shape_name}"] = prob

        # Add size predicates: is_small, is_large
        for idx, prob in enumerate(p_size):
            size_name = idx2size[idx]
            predicates[f"is_{size_name}"] = prob

        # Add material predicates: is_rubber, is_metal
        for idx, prob in enumerate(p_mat):
            mat_name = idx2mat[idx]
            predicates[f"is_{mat_name}"] = prob

        # Build object entry
        obj_entry = {
            "idx": obj_idx,                     # Object ID within the scene
            "position": feat_tensor.tolist(),   # Coordinates: [x, y, z]
            "predicates": predicates            # Dict of 15 soft-truth values
        }
        scene_objects.append(obj_entry)

    # Build the final scene grounding dictionary
    scene_dict = {
        "scene_id": scene_idx,
        "objects": scene_objects
    }

    # Save as JSON file
    out_path = os.path.join(OUT_DIR, f"scene_{scene_idx:04d}.json")
    with open(out_path, "w") as fp:
        json.dump(scene_dict, fp, indent=2)

    print(f"✓ Exported scene {scene_idx:04d} -> {out_path}")

print(f"\n All {len(all_scenes)} scenes exported successfully to {OUT_DIR}")
