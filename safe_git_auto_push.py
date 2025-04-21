
import subprocess

def safe_git_auto_push(commit_message="Auto log update from RSS log"):
    try:
        # Check if there are any changes
        status_output = subprocess.check_output(["git", "status", "--porcelain"]).decode().strip()
        if not status_output:
            print("🟡 No changes to commit.")
            return

        # Stage changes
        subprocess.run(["git", "add", "."], check=True)

        # Commit changes without emoji to avoid encoding issues
        subprocess.run(["git", "commit", "-m", commit_message], check=True)

        # Push changes
        subprocess.run(["git", "push"], check=True)

        print("✅ Auto-push successful.")

    except subprocess.CalledProcessError as e:
        print(f"❌ Git command failed: {e}")
    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")

# Example usage
if __name__ == "__main__":
    safe_git_auto_push()
