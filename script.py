# ===========================
# NS-FinalProject-404 : Run Full Pipeline
# ===========================

import subprocess
import os

BASE_PATH = "./code"

# python files path
SCRIPTS = [
    f"{BASE_PATH}/1-Flow_Capture/flow_capture.py",
    f"{BASE_PATH}/2-Flow_Dependency_Extractor/flow_dependency_extractor.py",
    f"{BASE_PATH}/2-Flow_Dependency_Extractor/flow_dependency_twolevel.py",
    f"{BASE_PATH}/2-Flow_Dependency_Extractor/flow_dependency_multilevel.py",
    f"{BASE_PATH}/3-Bots_Detector/botnet_detector.py"
]

def run_step(script):
    print(f"\n[+] Running {script} ...")
    result = subprocess.run(["python", script], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("⚠️ ERRORS/Warnings:")
        print(result.stderr)

def main():
    total_steps = len(SCRIPTS)
    print("=== NS-FinalProject-404 script ===")
    for idx, script in enumerate(SCRIPTS, start=1):
        print(f"\n -> Step {idx}/{total_steps} started: {script}")
        if os.path.exists(script):
            run_step(script)
            print(f"-> Step {idx}/{total_steps} finished: {script}")
        else:
            print(f"❌ Script not found: {script}")
    print("\n✅ Pipeline script finished successfully!")

if __name__ == "__main__":
    main()
