"""
Setup script for the Japanese to English Translator application
"""

import os
import sys
import subprocess
import platform

def print_header(text):
    """Print a formatted header"""
    print("=" * 60)
    print(f"{text:^60}")
    print("=" * 60)

def check_python_version():
    """Check if Python version meets requirements"""
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 8):
        print(f"Error: Python 3.8 or higher is required. You have {major}.{minor}.")
        return False
    print(f"✓ Python version {major}.{minor} detected")
    return True

def check_ollama_installed():
    """Check if Ollama is installed and running"""
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✓ Ollama is installed")
            return True
        else:
            print("✗ Ollama is not installed or not accessible from command line")
            return False
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Ollama is not installed or not accessible from command line")
        return False

def check_model_available(model_name="lauchacarro/qwen2.5-translator:latest"):
    """Check if the required model is available in Ollama"""
    try:
        result = subprocess.run(['ollama', 'list'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            available_models = result.stdout
            if model_name in available_models:
                print(f"✓ Model {model_name} is available")
                return True
            else:
                print(f"✗ Model {model_name} is not available. You need to pull it first.")
                return False
        else:
            print("✗ Could not check available models")
            return False
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Could not check available models")
        return False

def install_model(model_name="lauchacarro/qwen2.5-translator:latest"):
    """Install the required model"""
    try:
        print(f"Pulling model {model_name}...")
        result = subprocess.run(['ollama', 'pull', model_name], 
                              capture_output=True, text=True, timeout=300)  # 5 minute timeout
        if result.returncode == 0:
            print(f"✓ Model {model_name} installed successfully")
            return True
        else:
            print(f"✗ Failed to install model: {result.stderr}")
            return False
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"✗ Failed to install model: {e}")
        return False

def install_conda_environment():
    """Install the conda environment"""
    try:
        print("Creating conda environment...")
        result = subprocess.run([
            'conda', 'env', 'create', '-f', 'environment.yml'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Conda environment created successfully")
            print("\nTo activate the environment, run:")
            print("conda activate txt_translator")
            return True
        else:
            print(f"✗ Failed to create conda environment: {result.stderr}")
            return False
    except FileNotFoundError:
        print("✗ Conda not found. Please install Anaconda or Miniconda first.")
        return False

def install_pip_requirements():
    """Install pip requirements"""
    try:
        print("Installing pip requirements...")
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Pip requirements installed successfully")
            return True
        else:
            print(f"✗ Failed to install pip requirements: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Failed to install pip requirements: {e}")
        return False

def main():
    print_header("Japanese to English Translator Setup")
    print()
    
    # Check Python version
    if not check_python_version():
        return False
    
    print()
    
    # Check Ollama installation
    ollama_ok = check_ollama_installed()
    if not ollama_ok:
        print("\nPlease install Ollama from https://ollama.com/ before continuing.")
        return False
    
    print()
    
    # Check model availability
    model_ok = check_model_available()
    if not model_ok:
        response = input("Would you like to install the required model now? (y/n): ")
        if response.lower() in ['y', 'yes']:
            if not install_model():
                return False
        else:
            print("Please install the model manually using: ollama pull lauchacarro/qwen2.5-translator:latest")
            return False
    
    print()
    
    # Ask about conda vs pip installation
    print("Choose your preferred installation method:")
    print("1. Conda environment (recommended)")
    print("2. Pip in current environment")
    
    choice = input("Enter your choice (1 or 2): ").strip()
    
    print()
    
    if choice == "1":
        success = install_conda_environment()
    elif choice == "2":
        success = install_pip_requirements()
    else:
        print("Invalid choice. Please run the setup again.")
        return False
    
    if success:
        print()
        print_header("Setup Complete!")
        print("✓ Python version is compatible")
        print("✓ Ollama is installed and running")
        print("✓ Required model is available")
        if choice == "1":
            print("✓ Conda environment created (remember to activate it)")
        else:
            print("✓ Required packages installed")
        print()
        print("To run the application:")
        if choice == "1":
            print("1. Activate your conda environment: conda activate txt_translator")
        print("2. Run: python run_app.py")
        print()
        print("Alternatively, you can use the batch file: run_translator.bat")
        return True
    else:
        print()
        print_header("Setup Failed!")
        print("Please review the error messages above and try again.")
        return False

if __name__ == "__main__":
    main()