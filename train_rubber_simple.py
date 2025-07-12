import json
import torch
from torch import nn, optim
import matplotlib.pyplot as plt
import ltn
from z3 import Solver, Real

# ─── 1) Load CLEVR val scenes ──────────────────────────────────────────────────
with open("CLEVR_v1.0/scenes/CLEVR_val_scenes.json","r") as f:
    data = json.load(f)["scenes"]

# ─── 2) Define neural “rubberness” and “metalness” nets ───────────────────────
class RubberNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(1, 1)
    def forward(self, x):
        return torch.sigmoid(self.fc(x)).squeeze(1)  # → [N]

class MetalNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(1,1)
    def forward(self, x):
        return torch.sigmoid(self.fc(x)).squeeze(1)  # → [N]

rubber_net = RubberNet()
metal_net  = MetalNet()
opt = optim.Adam(list(rubber_net.parameters()) + list(metal_net.parameters()), lr=1e-2)

# ─── 3) Training loop with fuzzy‐logic loss ───────────────────────────────────
epochs = 5
avg_sat_list, avg_loss_list = [], []

for epoch in range(1, epochs+1):
    total_loss = 0.0
    total_sat  = 0.0
    count      = 0

    for scene in data:
        objs = scene["objects"]
        N    = len(objs)
        if N < 2: 
            continue

        # x‐coords and ground‐truth metal mask
        xs = torch.tensor([[o["3d_coords"][0]] for o in objs], dtype=torch.float32)  # [N,1]
        # Predict
        pred_rub = rubber_net(xs)   # [N]
        pred_met = metal_net(xs)    # [N]
        
        # Fuzzy‐implication: (rubber_i ∧ metal_j) → left
        for i in range(N):
            for j in range(N):
                if i == j: continue
                left_ij = 1.0 if xs[i] < xs[j] else 0.0
                sat_ij  = pred_rub[i] * pred_met[j] * left_ij
                total_loss += (1.0 - sat_ij)
                total_sat  += sat_ij.item()
                count     += 1

    # Backpropagate average loss
    opt.zero_grad()
    (total_loss / count).backward()
    opt.step()

    avg_sat  = total_sat / count              # this is already a Python float
    avg_loss = (total_loss / count).item()    # .item() gives a float

    avg_sat_list.append(avg_sat)
    avg_loss_list.append(avg_loss)
    print(f"Epoch {epoch:>2}: avg_sat = {avg_sat:.4f}, avg_loss = {avg_loss:.4f}")

# ─── 4) Plot training curves ──────────────────────────────────────────────────
epochs_range = list(range(1, epochs+1))
plt.figure()
plt.plot(epochs_range, avg_sat_list, marker='o')
plt.title("Avg Logic Satisfaction over Epochs")
plt.xlabel("Epoch")
plt.ylabel("Avg Satisfaction")
plt.grid(True)
plt.figure()
plt.plot(epochs_range, avg_loss_list, marker='o')
plt.title("Avg Logic Loss over Epochs")
plt.xlabel("Epoch")
plt.ylabel("Avg Loss")
plt.grid(True)

plt.show()

# ─── 5) Save & reload into LTNtorch predicates ───────────────────────────────
torch.save(rubber_net.state_dict(), "rubber_net.pt")
torch.save(metal_net.state_dict(),  "metal_net.pt")

# Wrapper classes for LTN
class RubberLTNModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = RubberNet()
        self.net.load_state_dict(torch.load("rubber_net.pt"))
    def forward(self, x, idx):
        i = idx.item() if not hasattr(idx, "value") else idx.value.item()
        return self.net(x)[i]

class MetalLTNModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = MetalNet()
        self.net.load_state_dict(torch.load("metal_net.pt"))
    def forward(self, x, idx):
        i = idx.item() if not hasattr(idx, "value") else idx.value.item()
        return self.net(x)[i]

class LeftOfModel(nn.Module):
    def forward(self, x1, x2):
        return (x1 < x2).float()

RubberLTN = ltn.Predicate(RubberLTNModel())
MetalLTN  = ltn.Predicate(MetalLTNModel())
LeftOf    = ltn.Predicate(LeftOfModel())

# Evaluate LTN logic satisfaction across scenes
ltotal, lcount = 0.0, 0
for scene in data:
    objs = scene["objects"]; N=len(objs)
    if N<2: continue
    coords = torch.tensor([[o["3d_coords"][0]] for o in objs], dtype=torch.float32)
    X_data = ltn.Constant(coords)
    for i in range(N):
        for j in range(N):
            if i==j: continue
            r = RubberLTN(X_data, ltn.Constant(torch.tensor(i))).value
            m = MetalLTN (X_data, ltn.Constant(torch.tensor(j))).value
            l = LeftOf   (ltn.Constant(coords[i].unsqueeze(0)), ltn.Constant(coords[j].unsqueeze(0))).value
            sat = (r * m * l).item()
            ltotal  += sat
            lcount  += 1
print(f"LTN Logic Satisfaction (loaded nets): {ltotal/lcount:.4f}")

# ─── 6) Z3 Synthesis Example ──────────────────────────────────────────────────
x_r, x_m = Real("x_r"), Real("x_m")
s = Solver()
s.add(x_r < x_m)
if s.check().r == s.check().r.sat:
    m = s.model()
    print("Z3 example:", m[x_r], "<", m[x_m])

# ─── 7) Additional Rule: “Large red spheres left of blue cubes” ───────────────
vals = []
for scene in data:
    for o1 in scene["objects"]:
        if o1["color"]=="red" and o1["shape"]=="sphere" and o1["size"]=="large":
            x1 = o1["3d_coords"][0]
            for o2 in scene["objects"]:
                if o2["color"]=="blue" and o2["shape"]=="cube":
                    x2 = o2["3d_coords"][0]
                    vals.append(1.0 if x1 < x2 else 0.0)
if vals:
    print("Rule ‘large red spheres left of blue cubes’ sat:", sum(vals)/len(vals))
else:
    print("No pairs for red-sphere/blue-cube rule found.")
