import subprocess

def sync_logs_to_github():
    try:
        subprocess.run(["git", "add", "scholar_logs.csv", "bonus_logs.csv"], check=True)
        subprocess.run(["git", "commit", "-m", "🔁 Auto-sync logs from Streamlit app"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Logs pushed to GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git push failed: {e}")
