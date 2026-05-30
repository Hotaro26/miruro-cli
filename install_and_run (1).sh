#!/bin/bash

# 1. Setup paths and Repository
REPO_URL="https://github.com/Hotaro26/miruro-cli.git"
APP_DIR="miruro_app_deploy"

echo "Cloning repository from $REPO_URL..."
if [ -d "$APP_DIR" ]; then
    echo "Directory $APP_DIR already exists. Updating..."
    rm -rf "$APP_DIR"
fi

git clone "$REPO_URL" "$APP_DIR"
cd "$APP_DIR"

# 2. Check and install mpv
if ! command -v mpv &> /dev/null; then
    echo "mpv not found. Attempting to install..."
    sudo apt-get update && sudo apt-get install -y mpv || echo "Warning: Could not install mpv."
else
    echo "mpv is already installed."
fi

# 3. Create virtual environment
echo "Configuring virtual environment..."
python3 -m venv venv

# 4. Install dependencies using the venv's pip directly
echo "Installing requirements..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt
./venv/bin/playwright install chromium

# 5. Determine activation command based on shell
echo "--- Starting Miruro CLI ---"
if [[ "$SHELL" == *"fish"* ]]; then
    ./venv/bin/python main.py
else
    source venv/bin/activate
    python main.py
fi