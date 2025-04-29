import subprocess
import os
from datetime import datetime

def configure_git_user():
    """Ensure Git user configuration is set globally."""
    try:
        subprocess.run(["git", "config", "--global", "user.name", "MAPULVER1"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "michaelalexanderpulver@outlooks.com"], check=True)
        print("✅ Git user configuration set successfully.")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Failed to configure Git user: {e}")


def run_git_command(command, description):
    """Run a Git command with error handling."""
    try:
        subprocess.run(command, check=True)
        print(f"✅ {description} successful.")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ {description} failed: {e}")
