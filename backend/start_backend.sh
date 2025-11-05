#!/bin/bash
# Start the Investment Research Assistant backend

cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Start the server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
