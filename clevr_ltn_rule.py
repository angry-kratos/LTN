import json
import os
import torch
import ltn

# Load CLEVR validation scenes. The CLEVR dataset location can be provided via
# the CLEVR_DIR environment variable. By default we look for a local
# ``CLEVR_v1.0`` directory.
clevr_dir = os.getenv("CLEVR_DIR", "CLEVR_v1.0")
scenes_path = os.path.join(clevr_dir, "scenes", "CLEVR_val_scenes.json")
with open(scenes_path, "r") as f:
    data = json.load(f)

class RubberModelLearnable(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = torch.nn.Linear(1, 1)

    def forward(self, x, idx):
        # Safely get the index
        i = idx.value.item() if hasattr(idx, "value") else idx.item()

        # Ensure x[i] is [1] and convert to shape [1, 1]
        x_i = x[i].unsqueeze(0)  # [1, 1]

        # Pass through linear layer
        out = self.fc(x_i)       # [1, 1]

        # Apply sigmoid and squeeze to scalar
        return torch.sigmoid(out).squeeze()  # shape: []




# Fixed metal predicate
class MetalModel(torch.nn.Module):
    def forward(self, x, idx):
        return torch.tensor([
            1.0 if materials[i.item()] == 'metal' else 0.0 for i in idx
        ], dtype=torch.float32)

# Spatial predicate: is_left(x1, x2)
class LeftOfModel(torch.nn.Module):
    def forward(self, x1, x2):
        return (x1 < x2).float()

Rubber = ltn.Predicate(RubberModelLearnable())
Metal = ltn.Predicate(MetalModel())
LeftOf = ltn.Predicate(LeftOfModel())

optimizer = torch.optim.Adam(Rubber.parameters(), lr=0.01)
epochs = 5

for epoch in range(epochs):
    total_loss = 0
    truth_vals = []

    for scene in data['scenes']:
        objects = scene['objects']

        features = []
        materials = []

        for obj in objects:
            x = obj['3d_coords'][0]
            features.append([x])
            materials.append(obj['material'])

        if len(features) < 2:
            continue

        features = torch.tensor(features, dtype=torch.float32)
        X_data = ltn.Constant(features)

        for i in range(len(features)):
            for j in range(len(features)):
                if i == j:
                    continue

                xi = ltn.Constant(features[i].unsqueeze(0))
                xj = ltn.Constant(features[j].unsqueeze(0))
                idx_i = ltn.Constant(torch.tensor(i))
                idx_j = ltn.Constant(torch.tensor(j))

                pred_rubber = Rubber(X_data, idx_i).value
                pred_metal = Metal(X_data, idx_j).value
                pred_left = LeftOf(xi, xj).value

                implication = pred_rubber * pred_metal * pred_left
                logic_loss = 1 - implication

                total_loss += logic_loss
                truth_vals.append(implication.item())

    optimizer.zero_grad()
    total_loss.backward()
    optimizer.step()

    avg_satisfaction = sum(truth_vals) / len(truth_vals) if truth_vals else 1.0
    print(f"Epoch {epoch+1}: Logic Satisfaction = {avg_satisfaction:.4f}")
