#!/usr/bin/env python
"""Runner script to execute setup_jwt_complete.py without PowerShell"""
import subprocess
import sys
import os

# Change to dashboard directory
os.chdir(r'e:\djangoproject\student_dashboard\dashboard')

# Run the setup script
print("Starting JWT Complete Setup...\n")
result = subprocess.run([sys.executable, 'setup_jwt_complete.py'], capture_output=False)
sys.exit(result.returncode)
