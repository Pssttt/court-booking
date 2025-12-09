#!/bin/bash

set -e

cd "$(dirname "$0")"

echo "Court Booking WebApp"
echo "======================="

if ! command -v python3 &>/dev/null; then
  echo "Python 3 not found. Please install Python 3.9+"
  exit 1
fi

if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

source venv/bin/activate

echo "Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "Ready to start!"
echo "Opening http://localhost:3000"
echo "Edit config/settings.py to customize"
echo ""

python main.py
