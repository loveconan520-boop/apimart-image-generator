#!/usr/bin/env python3
import subprocess
import sys

# Kill existing python processes
subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], capture_output=True)

# Start the server
subprocess.run([sys.executable, 'app.py'])
