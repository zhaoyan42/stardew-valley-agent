import os
import json
import time
import logging
from dotenv import load_dotenv
from brain.agent import StardewAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
STATUS_PATH = "status.json"
COMMANDS_PATH = "commands.json"
TACTICS_PATH = "tactics.json"
LOGS_PATH = "daily_logs.json"

def load_config():
    load_dotenv()
    provider = os.getenv("LLM_PROVIDER", "openai")
    api_key = os.getenv("OPENAI_API_KEY") if provider == "openai" else os.getenv("ANTHROPIC_API_KEY")
    return provider, api_key

def main():
    logger.info("Starting Stardew Valley AI Agent Main Loop...")
    
    provider, api_key = load_config()
    if not api_key:
        logger.error("API Key not found. Please run 'python brain/init_wizard.py' first.")
        return

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
                    
                    # Reset review flag for new day
                    if game_day != current_day:
                        current_day = game_day
                        day_reviewed = False
                        logger.info(f"--- Start of Day {game_day} ---")

                    # Morning Plan (AM 6:00)
                    if game_time == 600:
                        logger.info("It's early morning. Generating daily plan...")
                        # In a real scenario, we might have a screenshot
                        screenshot_path = "screenshot.png"
                        if not os.path.exists(screenshot_path):
                            screenshot_path = None
                        
                        plan = agent.decide_action(image_path=screenshot_path)
                        logger.info(f"Morning Plan: {plan}")

                    # Evening Review (PM 10:00+)
                    elif game_time >= 2200 and not day_reviewed:
                        logger.info("It's late evening. Reviewing the day...")
                        daily_logs = []
                        if os.path.exists(LOGS_PATH):
                            with open(LOGS_PATH, 'r', encoding='utf-8') as f:
                                daily_logs = json.load(f)
                        
                        review = agent.review_day(daily_logs)
                        logger.info(f"Daily Review: {review}")
                        day_reviewed = True
                    
                    # Normal tactical decision if requested or based on state
                    # For now, we'll just react to status updates
                    else:
                        logger.info(f"Status update received at {game_time}. Agent observing...")
                        # agent.decide_action() # Optional: decide something every status update

            else:
                # logger.info("Waiting for status.json from Mod...")
                pass

        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
        
        time.sleep(2) # Poll every 2 seconds

if __name__ == "__main__":
    main()
