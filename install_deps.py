#!/usr/bin/env python
"""
Script to install required dependencies for the translator app

This script will remove any existing 'screen-translator' conda environment, create a fresh one from
`environment.yml`, and install pip packages from `requirements.txt` into the new environment.
"""

import subprocess
import sys
import os

ENV_NAME = "screen-translator"
ENV_FILE = "environment.yml"
REQ_FILE = "requirements.txt"


def run_cmd(cmd, check=True):
    try:
        subprocess.run(cmd, check=check)
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False


def remove_conda_env(env_name):
    print(f"Removing existing conda environment '{env_name}' if present...")
    try:
        subprocess.run(["conda", "env", "remove", "-n", env_name, "-y"], check=True)
        print("Removed existing environment (if it existed).")
    except subprocess.CalledProcessError:
        print("Failed to remove environment (it may not exist). Continuing...")
    except FileNotFoundError:
        print("Conda not found. Please install conda first.")
        return False
    return True


def install_conda_env():
    print(f"Creating conda environment from {ENV_FILE} as '{ENV_NAME}' ...")
    if not run_cmd(["conda", "env", "create", "-f", ENV_FILE]):
        print("Failed to create conda environment. Ensure conda is installed and environment.yml is valid.")
        return False
    print("Conda environment created successfully.")
    return True


def install_pip_deps_in_env():
    print(f"Installing pip dependencies into '{ENV_NAME}'...")
    try:
        subprocess.check_call(["conda", "run", "-n", ENV_NAME, "python", "-m", "pip", "install", "-r", REQ_FILE])
        print("Pip dependencies installed successfully inside the conda env.")
        return True
    except subprocess.CalledProcessError:
        print("Failed to install pip dependencies into the conda environment.")
        return False
    except FileNotFoundError:
        print("Conda not found. Please install conda first.")
        return False


def main():
    print("Setting up the Translator environment...")

    # Remove existing env (user requested a fresh install)
    if not remove_conda_env(ENV_NAME):
        print("Could not remove environment. Aborting.")
        return

    if not install_conda_env():
        return

    # Install pip requirements into the newly created env
    install_pip_deps_in_env()

    print("\nDone. To use the environment:")
    print(f"  conda activate {ENV_NAME}")
    print("Then run the application, e.g:")
    print("  python run_app.py")

if __name__ == "__main__":
    main()