from mem0 import Memory
import os
import time
import subprocess
import sys

class MemoryManager:
    def __init__(self, db_path="./mem0_db"):
        self.db_path = os.path.abspath(db_path)
        # Ensure the directory exists
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path)

        # Explicitly configure qdrant to use a local project path instead of /tmp
        config = {
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "path": self.db_path,
                }
            }
        }

        try:
            self.memory = Memory.from_config(config)
        except RuntimeError as e:
            if "already accessed by another instance" in str(e):
                print(f"Warning: Qdrant lock detected. Attempting to force unlock...")
                if self._force_unlock():
                    # Retry after force unlock
                    try:
                        self.memory = Memory.from_config(config)
                        print("Successfully recovered from database lock.")
                        return
                    except Exception as re:
                        print(f"Retry failed: {re}")
                else:
                    print("Could not automatically resolve lock. Please close other instances of the agent.")
            raise e
        except Exception as e:
            print(f"Failed to initialize Memory: {e}")
            raise e

    def _force_unlock(self):
        """
        Attempts to kill other python processes that might be holding the Qdrant lock.
        Primarily for Windows.
        """
        import subprocess
        import sys

        current_pid = os.getpid()
        scripts_to_check = ["main.py", "mcp_server.py", "init_wizard.py", "agent.py"]

        if sys.platform == "win32":
            try:
                # Use powershell to find other python processes running our scripts
                # We exclude our own PID
                pattern = "|".join([s.replace(".", "\\.") for s in scripts_to_check])
                ps_cmd = (
                    f"$procs = Get-CimInstance Win32_Process | "
                    f"Where-Object {{ $_.Name -eq 'python.exe' -and $_.ProcessId -ne {current_pid} -and "
                    f"($_.CommandLine -match '{pattern}') }}; "
                    f"if ($procs) {{ $procs | ForEach-Object {{ taskkill /F /PID $_.ProcessId /T }} }}"
                )
                subprocess.run(["powershell", "-Command", ps_cmd], check=True, capture_output=True)

                # Also try to delete the lock file if it's still there
                lock_file = os.path.join(self.db_path, ".lock")
                if os.path.exists(lock_file):
                    # Small delay to let OS release handles
                    time.sleep(1)
                    try:
                        os.remove(lock_file)
                    except:
                        pass
                return True
            except Exception as e:
                print(f"Force unlock error: {e}")
                return False
        return False
    def add_memory(self, content, user_id):
        """
        Add a memory for a specific user.
        """
        return self.memory.add(content, user_id=user_id)

    def search_memory(self, query, user_id):
        """
        Search for memories for a specific user.
        """
        return self.memory.search(query, user_id=user_id)

if __name__ == "__main__":
    # Quick test
    manager = MemoryManager()
    manager.add_memory("The player prefers Parsnips for early game profit.", user_id="stardew_player_1")
    results = manager.search_memory("What should I plant early game?", user_id="stardew_player_1")
    print(results)
