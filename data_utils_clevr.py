
import json
import torch

def load_clevr_scenes(json_path):
    """
    Returns a list of scene dictionaries as given in CLEVR_val_scenes.json
    """
    with open(json_path, "r") as f:
        data = json.load(f)["scenes"]
    return data

def extract_object_data_for_scene(scene):
    """
    Given one CLEVR scene (a dict), return a list of tuples:
       (feature_tensor, label_dict)
    where:
      - feature_tensor is a torch.Tensor([x, y, z]) of shape [3].
      - label_dict is a dict: {"color": str, "shape": str, "size": str, "material": str}
    """
    obj_list = []
    for obj in scene["objects"]:
        coords = obj["3d_coords"]  # [x,y,z]
        feat   = torch.tensor(coords, dtype=torch.float32)  # shape = [3]
        labels = {
            "color":    obj["color"],
            "shape":    obj["shape"],
            "size":     obj["size"],
            "material": obj["material"]
        }
        obj_list.append((feat, labels))
    return obj_list

