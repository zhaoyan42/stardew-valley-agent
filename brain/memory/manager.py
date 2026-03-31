from mem0 import Memory
import os

class MemoryManager:
    def __init__(self, db_path="./mem0_storage"):
        self.db_path = db_path
        # Use default config for local storage
        self.memory = Memory()

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
