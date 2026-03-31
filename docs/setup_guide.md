# Stardew Valley AI Agent Setup Guide

This guide describes how to initialize and run the Stardew Valley AI Agent.

## Prerequisites
- Python 3.10+
- OpenAI or Anthropic API Key
- Stardew Valley SMAPI Mod (StardewValleyAI) installed

## Setup Instructions

1. **Initialize the Agent**
   Run the initialization wizard to configure your API keys and game preferences:
   ```bash
   python brain/init_wizard.py
   ```
   Follow the prompts to enter:
   - LLM Provider (openai/anthropic)
   - API Key
   - Base URL (if applicable)
   - Preferred Marriage Candidate
   - Farming Playstyle
   - Ultimate Goal

2. **Run the Main Agent**
   Ensure the game is running with the Mod installed. Then start the Python agent:
   ```bash
   python main.py
   ```

## Communication Logic
The Python agent communicates with the C# Mod via three JSON files:
- `status.json`: Read by Python to get the current game state.
- `commands.json`: Written by Python to send actions to the game.
- `tactics.json`: Updated by Python to adjust agent behavior.
- `daily_logs.json`: Read by Python for post-mortem analysis.

## Daily Cycle
1. **AM 6:00**: The agent generates a high-level daily plan based on the morning status.
2. **During the Day**: The agent monitors `status.json` and issues tactical commands.
3. **PM 10:00+**: The agent performs a daily review, updating `tactics.json` if necessary.
