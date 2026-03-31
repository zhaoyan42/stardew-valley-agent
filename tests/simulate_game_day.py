import json
import os
import time
from brain.agent import StardewAgent
from dotenv import load_dotenv

# Load environment
load_dotenv()

STATUS_PATH = "status.json"
COMMANDS_PATH = "commands.json"
TACTICS_PATH = "tactics.json"
LOGS_PATH = "daily_logs.json"

def simulate_morning(agent):
    print("\n--- Simulating Morning (AM 6:00) ---")
    status = {
        "timeOfDay": 600,
        "dayOfMonth": 1,
        "season": "spring",
        "money": 500,
        "energy": 270,
        "location": "FarmHouse",
        "inventory": []
    }
    with open(STATUS_PATH, 'w') as f:
        json.dump(status, f)
    
    print("Agent deciding morning plan...")
    plan = agent.decide_action()
    print(f"Plan: {plan}")
    
    if os.path.exists(COMMANDS_PATH):
        with open(COMMANDS_PATH, 'r') as f:
            cmd = json.load(f)
            print(f"Action issued: {json.dumps(cmd, indent=2)}")
    else:
        print("No command issued yet (expected if plan is just text).")

def simulate_evening(agent):
    print("\n--- Simulating Evening (PM 10:00) ---")
    status = {
        "timeOfDay": 2200,
        "dayOfMonth": 1,
        "season": "spring",
        "money": 800,
        "energy": 10,
        "location": "FarmHouse",
        "inventory": [{"name": "Parsnip Seed", "count": 5}]
    }
    with open(STATUS_PATH, 'w') as f:
        json.dump(status, f)

    logs = [
        {"time": 700, "action": "Watered crops", "result": "Success"},
        {"time": 1000, "action": "Foraged Daffodil", "result": "Success"},
        {"time": 1500, "action": "Fished at river", "result": "Failed (no energy)"},
        {"time": 1800, "action": "Talked to Pierre", "result": "Success"}
    ]
    with open(LOGS_PATH, 'w') as f:
        json.dump(logs, f)

    # Initial tactics
    initial_tactics = {
        "energy_threshold": 20,
        "priority": "profit"
    }
    with open(TACTICS_PATH, 'w') as f:
        json.dump(initial_tactics, f)

    print("Agent reviewing day...")
    review = agent.review_day(logs)
    print(f"Review: {review}")

    with open(TACTICS_PATH, 'r') as f:
        updated_tactics = json.load(f)
        print(f"Updated Tactics: {json.dumps(updated_tactics, indent=2)}")
        
        if updated_tactics != initial_tactics:
            print("[✓] Tactics evolved!")
        else:
            print("[!] Tactics did not change (this is possible if LLM thinks they are fine).")

if __name__ == "__main__":
    provider = os.getenv("LLM_PROVIDER", "openai")
    api_key = os.getenv("OPENAI_API_KEY") if provider == "openai" else os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("Error: API key not found in .env. Run init_wizard first or set it manually.")
    else:
        agent = StardewAgent(provider=provider, api_key=api_key)
        simulate_morning(agent)
        simulate_evening(agent)
