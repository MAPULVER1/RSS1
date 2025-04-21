
import subprocess
import os
from datetime import datetime

def safe_git_commit(message="Auto log update", files_to_commit=["."]):
    try:
        # Stage specified files
        subprocess.run(["git", "add"] + files_to_commit, check=True)

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
            f.write(f"FAILED GIT OPERATION\nMessage: {message}\nTime: {datetime.now()}\n")
        print(f"🕒 Change buffered to: {log_buffer_file}")
