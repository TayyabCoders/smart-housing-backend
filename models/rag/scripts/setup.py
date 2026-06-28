import os
import subprocess
import sys

def install_dependencies():
    print("🚀 Checking and installing dependencies...")
    # UV use ho raha hai to uv pip, warna normal pip
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully.")
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")

def run_app():
    print("🏢 Starting O.T.T.O Assistant...")
    try:
        # Aapki main file ka naam app.py hai
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n👋 O.T.T.O is shutting down. Goodbye!")

if __name__ == "__main__":
    # 1. Install/Update requirements
    if os.path.exists("requirements.txt"):
        install_dependencies()
    else:
        print("⚠️ requirements.txt not found. Skipping installation.")

    # 2. Launch the UI
    run_app()