
import os
import subprocess
import time

def run_git_command(cmd, retries=3, delay=2):
    """Run a git command with retries."""
    for attempt in range(retries):
        try:
            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Attempt {attempt + 1} failed for command: {' '.join(cmd)}. Error: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
    return False

def resync_pending_logs():
    buffer_dir = "pending_logs"
    if not os.path.exists(buffer_dir):
        print("✅ No pending logs to resync.")
        return

    files = sorted(os.listdir(buffer_dir))
    if not files:
        print("✅ No pending logs to resync.")
        return

    for fname in files:
        fpath = os.path.join(buffer_dir, fname)
        print(f"🔄 Attempting resync: {fname}")
        try:
            if not run_git_command(["git", "add", "."]):
                raise Exception("Failed to add changes to Git.")
            if not run_git_command(["git", "commit", "-m", f"Resync: {fname}"]):
                raise Exception("Failed to commit changes to Git.")
            if not run_git_command(["git", "push"]):
                raise Exception("Failed to push changes to remote repository.")
            
            os.remove(fpath)
            print(f"✅ Resynced and removed: {fname}")
        except Exception as e:
            print(f"❌ Failed to resync {fname}: {e}")
