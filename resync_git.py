
import os
import subprocess

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
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", f"Resync: {fname}"], check=True)
            subprocess.run(["git", "push"], check=True)
            os.remove(fpath)
            print(f"✅ Resynced and removed: {fname}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to resync {fname}: {e}")
