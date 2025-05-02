import subprocess
import os

def safe_git_auto_push(commit_message="Auto log update from RSS log", repo_path="."):
    try:
        # Navigate to the repository path
        os.chdir(repo_path)

        # Check if there are any changes
        status_output = subprocess.check_output(["git", "status", "--porcelain"]).decode().strip()
        if not status_output:
            print(f"🟡 No changes to commit in {repo_path}.")
            return

        # Stage changes
        subprocess.run(["git", "add", "."], check=True)

        # Commit changes without emoji to avoid encoding issues
        subprocess.run(["git", "commit", "-m", commit_message], check=True)

        # Push changes
        subprocess.run(["git", "push"], check=True)

        print(f"✅ Auto-push successful for {repo_path}.")

        # Verify logs are accessible
        log_output = subprocess.check_output(["git", "log", "--oneline"]).decode().strip()
        print(f"📜 Recent logs for {repo_path}:\n{log_output}")

    except subprocess.CalledProcessError as e:
        print(f"❌ Git command failed in {repo_path}: {e}")
    except Exception as e:
        print(f"⚠️ Unexpected error in {repo_path}: {e}")

def push_updates_system_wide(directories, commit_message="Auto log update from RSS log"):
    for repo_path in directories:
        if os.path.isdir(repo_path) and os.path.exists(os.path.join(repo_path, ".git")):
            safe_git_auto_push(commit_message, repo_path)
        else:
            print(f"⚠️ Skipping {repo_path}: Not a valid Git repository.")

# Example usage
if __name__ == "__main__":
    # List of directories containing Git repositories
    repositories = ["/MAPULVER1/RSS1", "/path/to/another/repo"]
    push_updates_system_wide(repositories)
