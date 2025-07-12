#!/bin/bash

VSCODE_CLI="/Applications/Visual Studio Code.app/Contents/Resources/app/bin"
ENV_PATH="$HOME/miniconda3/envs/ltn_env"

mkdir -p $ENV_PATH/etc/conda/activate.d

echo 'export PATH="'$VSCODE_CLI':$PATH"' > $ENV_PATH/etc/conda/activate.d/env_vars.sh

echo "✅ VS Code CLI added to ltn_env"
echo "➡️  Please run: conda deactivate && conda activate ltn_env"
