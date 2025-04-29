import subprocess
import os
from datetime import datetime

def safe_git_commit(message="Auto log update", files_to_commit=["."]):
    try:
        # Ensure the current directory is a Git repository
        result = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], check=True, capture_output=True, text=True)
        if result.stdout.strip() != "true":
            raise Exception("Not a valid Git repository.")

        # Stage specified files
        subprocess.run(["git", "add"] + files_to_commit, check=True)

        # Check if there are changes to commit
        status_result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if not status_result.stdout.strip():
            print("⚠️ No changes to commit.")
            return

        # Attempt commit
        subprocess.run(["git", "commit", "-m", message], check=True)

        # Attempt push
        subprocess.run(["git", "push"], check=True)

        print("✅ Git commit and push successful.")

    except subprocess.CalledProcessError as e:
        print(f"⚠️ Git operation failed: {e}")
        log_buffer_file = f"pending_logs/git_buffer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        os.makedirs("pending_logs", exist_ok=True)
        with open(log_buffer_file, "w") as f:
            f.write(f"FAILED GIT OPERATION\nMessage: {message}\nTime: {datetime.now()}\nError: {e}\n")
        print(f"🕒 Change buffered to: {log_buffer_file}")

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
