import os
import json
from dotenv import set_key
from brain.memory.manager import MemoryManager

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def init_wizard():
    print("==========================================")
    print("   Stardew Valley AI Agent Init Wizard   ")
    print("==========================================\n")
    
    # 1. API Configuration
    print("--- 1. API Configuration ---")
    provider = input("Choose LLM provider (openai/anthropic) [default: openai]: ").strip().lower() or "openai"
    api_key = input(f"Enter your {provider.upper()} API Key: ").strip()
    base_url = input(f"Enter {provider.upper()} Base URL (optional, press Enter for default): ").strip()

    env_path = os.path.join(os.getcwd(), ".env")
    if provider == "openai":
        set_key(env_path, "OPENAI_API_KEY", api_key)
        if base_url:
            set_key(env_path, "OPENAI_BASE_URL", base_url)
    else:
        set_key(env_path, "ANTHROPIC_API_KEY", api_key)
        if base_url:
            set_key(env_path, "ANTHROPIC_BASE_URL", base_url)
    
    set_key(env_path, "LLM_PROVIDER", provider)
    print(f"\n[✓] API configuration saved to .env\n")

    # 2. Long-term Planning Preferences
    print("--- 2. Long-term Planning Preferences ---")
    spouse = input("Who is your preferred marriage candidate? (e.g., Abigail, Leah, Sebastian): ").strip()
    style = input("What is your farming style? (e.g., Min-max profit, Aesthetic/Relaxed, Animal-focused): ").strip()
    goal = input("What is your ultimate goal? (e.g., Perfection, Community Center in Year 1, 10 Million Gold): ").strip()

    preferences = {
        "marriage_candidate": spouse,
        "playstyle": style,
        "ultimate_goal": goal
    }

    # Store in Mem0
    print("\nSaving preferences to long-term memory...")
    memory_manager = MemoryManager()
    user_id = "stardew_player_1"
    
    memory_content = f"Player Preferences: Preferred Spouse: {spouse}, Playstyle: {style}, Ultimate Goal: {goal}"
    memory_manager.add_memory(memory_content, user_id=user_id)
    
    print("[✓] Preferences saved to memory database.\n")

    print("==========================================")
    print("   Setup Complete! You are ready to go.  ")
    print("   Run 'python main.py' to start.        ")
    print("==========================================")

if __name__ == "__main__":
    init_wizard()
