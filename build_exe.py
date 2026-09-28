"""
Build script to compile CollegeLab AI Agent into a standalone Windows executable: CollegeLabAI.exe
Uses PyInstaller.
"""

import os
import sys
import subprocess
import shutil

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def build_executable():
    print("=" * 60)
    print("Compiling CollegeLab AI Agent -> CollegeLabAI.exe")
    print("=" * 60)

    # PyInstaller options
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--name=CollegeLabAI",
        "--onefile",
        "--windowed",
        "--hidden-import=psutil",
        "--hidden-import=sqlite3",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=ctypes",
        f"--paths={PROJECT_ROOT}",
        os.path.join(PROJECT_ROOT, "main.py")
    ]

    print(f"Executing: {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=PROJECT_ROOT)
    
    if proc.returncode == 0:
        dist_exe = os.path.join(PROJECT_ROOT, "dist", "CollegeLabAI.exe")
        if os.path.exists(dist_exe):
            size_mb = round(os.path.getsize(dist_exe) / (1024 * 1024), 2)
            print("=" * 60)
            print(f"BUILD SUCCESSFUL!")
            print(f"Target Executable: {dist_exe}")
            print(f"Binary Size: {size_mb} MB")
            print("=" * 60)
            return True
    
    print("[ERROR] Build failed.")
    return False

if __name__ == "__main__":
    success = build_executable()
    sys.exit(0 if success else 1)
