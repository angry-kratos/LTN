# Mini LTN Pipeline

This folder `mini_pipeline` contains a minimal reimplementation of the neural-symbolic reasoning workflow. It shows how to go from simple scene descriptions to synthesized rules.

## Running
```bash
python3 mini_pipeline/run_pipeline.py
```

The script loads example scenes from `mini_pipeline/sample_scenes.json`, computes trivial predicate groundings, synthesizes a couple of rules, verifies them, ranks them, and prints a short summary.

## Requirements
Install dependencies with:
```bash
pip install -r requirements.txt
```
