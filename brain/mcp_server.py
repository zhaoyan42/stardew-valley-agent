import json
import os
from mcp.server.fastmcp import FastMCP
from brain.memory.manager import MemoryManager
from brain.memory.wiki_loader import WikiLoader

# Initialize FastMCP server
mcp = FastMCP("StardewValleyBrain")

# Constants for file paths
STATUS_PATH = os.path.join(os.getcwd(), "status.json")
COMMANDS_PATH = os.path.join(os.getcwd(), "commands.json")
TACTICS_PATH = os.path.join(os.getcwd(), "tactics.json")

# Initialize managers
memory_manager = MemoryManager()
wiki_loader = WikiLoader()

@mcp.tool()
def get_farm_state() -> str:
    """Returns the current game state including player stats, location, and farm status (json)."""
    if not os.path.exists(STATUS_PATH):
        return json.dumps({"error": "status.json not found", "path": STATUS_PATH})
    try:
        with open(STATUS_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return json.dumps(data, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_memory(query: str, user_id: str = "stardew_player_1") -> str:
    """Searches long-term memory for relevant past experiences or player preferences."""
    try:
        results = memory_manager.search_memory(query, user_id=user_id)
        return json.dumps(results, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_wiki_info(path: str) -> str:
    """
    Retrieves Stardew Valley wiki data. 
    Paths: 'summary' (all categories), 'crops' (crop list), 'crops/parsnip' (specific details).
    """
    try:
        parts = path.split('/')
        if parts[0] == 'summary':
            return wiki_loader.get_l0_summary()
        elif len(parts) == 1:
            return wiki_loader.get_l1_toc(parts[0])
        elif len(parts) == 2:
            return wiki_loader.get_l2_details(parts[0], parts[1])
        else:
            return "Invalid wiki path format. Use 'summary', 'category', or 'category/topic'."
    except Exception as e:
        return f"Error fetching wiki info: {str(e)}"

@mcp.tool()
def execute_action(action_json: str) -> str:
    """Dispatches a tactical action command (json) to the game mod."""
    try:
        # Validate JSON
        data = json.loads(action_json)
        with open(COMMANDS_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return f"Action successfully written to {COMMANDS_PATH}"
    except Exception as e:
        return f"Error writing action: {str(e)}"

@mcp.tool()
def update_tactics(config_json: str) -> str:
    """Updates the strategic configuration parameters (json) in tactics.json."""
    try:
        # Validate JSON
        data = json.loads(config_json)
        with open(TACTICS_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return f"Tactics successfully updated in {TACTICS_PATH}"
    except Exception as e:
        return f"Error updating tactics: {str(e)}"

if __name__ == "__main__":
    mcp.run()
