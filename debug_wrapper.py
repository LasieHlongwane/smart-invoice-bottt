import subprocess
import os
import sys
import time

exe_path = os.path.join(os.path.dirname(__file__), "LAC_Invoice_Pro_Debug.exe")

print("Running debug EXE...\n")
time.sleep(1)

try:
    subprocess.run([exe_path], check=True)
except Exception as e:
    print("\n\n❌ ERROR:")
    print(e)

print("\n\nPress ENTER to close...")
input()
