import os
import json
import time
import logging
from dotenv import load_dotenv

# Ensure environment variables are loaded immediately
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
STATUS_PATH = "status.json"
COMMANDS_PATH = "commands.json"
TACTICS_PATH = "tactics.json"
LOGS_PATH = "daily_logs.json"

def main():
    logger.info("Starting Stardew Valley AI Agent Main Loop...")
    
    provider = os.getenv("LLM_PROVIDER", "openai")
    api_key = os.getenv("OPENAI_API_KEY") if provider == "openai" else os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        logger.error("API Key not found. Please run 'python brain/init_wizard.py' first.")
        return

    # Deferred import to ensure env vars are ready
    from brain.agent import StardewAgent
    agent = StardewAgent(provider=provider, api_key=api_key)
    
    last_mod_time = 0
    day_reviewed = False
    current_day = -1

    while True:
        try:
            if os.path.exists(STATUS_PATH):
                mod_time = os.path.getmtime(STATUS_PATH)
                if mod_time > last_mod_time:
                    last_mod_time = mod_time
                    
                    with open(STATUS_PATH, 'r', encoding='utf-8') as f:
                        status = json.load(f)
                    
                    game_time = status.get("timeOfDay", 600)
                    game_day = status.get("dayOfMonth", 1)
                    
                    if game_day != current_day:
                        current_day = game_day
                        day_reviewed = False
                        logger.info(f"New day detected: Day {game_day}")

                    # Morning Plan (6:00 AM)
                    if game_time == 600 and not os.path.exists(COMMANDS_PATH):
                        logger.info("Generating morning plan...")
                        screenshot_path = "screenshot.png" # Mod should provide this
                        plan = agent.decide_action(image_path=screenshot_path)
                        logger.info(f"Morning Plan: {plan}")

                    # Night Review (10:00 PM+)
                    if game_time >= 2200 and not day_reviewed:
                        logger.info("Performing daily review...")
                        if os.path.exists(LOGS_PATH):
                            with open(LOGS_PATH, 'r', encoding='utf-8') as f:
                                daily_logs = json.load(f)
                            report = agent.review_day(daily_logs)
                            logger.info(f"Daily Report: {report}")
                            day_reviewed = True

            time.sleep(5) # Poll every 5 seconds
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
