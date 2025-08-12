#!/usr/bin/env bash
# -------------------------------------------------------------
# run.sh – create/activate venv, install deps, run pipeline,
#          then run evaluation
# -------------------------------------------------------------
set -e  # abort immediately if a command fails

# 1️⃣  Create virtual environment (if it doesn't exist yet)
if [[ ! -d ".venv" ]]; then
  echo "Creating virtual environment …"
  python -m venv .venv
fi

# 2️⃣  Activate it
#    (source will work on Bash, Zsh, etc.)
source .venv/bin/activate
echo "Virtual environment activated"

# 3️⃣  Upgrade pip (recommended)
pip install -U pip

# 4️⃣  Install the two requirement files
echo "Installing starter requirements …"
pip install -r starter/requirements.txt

echo "Installing agent requirements …"
pip install -r agent/requirements.txt

# 5️⃣  Run the pipeline
echo "Running agent/pipeline.py …"
python agent/pipeline.py

# 6️⃣  Run the evaluation script
echo "Running starter/eval.py …"
python starter/eval.py

echo "✅ Finished"