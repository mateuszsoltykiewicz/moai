#!/bin/bash
set -e

# Create venv if it doesn't exist
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# Activate venv
# shellcheck disable=SC1091
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r ./requirements.txt

# Export token
#export GITLAB_TOKEN=glpat-1ozxFpCi_8yH7iaghx7i

# Run the script (pass all arguments)
python ./images-controller.py
EXIT_CODE=$?

# Deactivate venv (for POSIX shells)
deactivate || true

# Remove the virtual environment directory
rm -rf .venv

exit $EXIT_CODE
