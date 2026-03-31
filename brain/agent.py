import json
import os
import base64
import imghdr
from openai import OpenAI
from anthropic import Anthropic
from brain.memory.manager import MemoryManager
from brain.mcp_server import get_farm_state, get_memory, get_wiki_info, execute_action, update_tactics

class StardewAgent:
    def __init__(self, provider="openai", api_key=None):
        self.provider = provider
        self.memory_manager = MemoryManager()
        
        if provider == "openai":
            self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
            self.model = "gpt-4o"
        elif provider == "anthropic":
            self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
            self.model = "claude-3-5-sonnet-20240620"
        
        self.tools = [
            {
                "name": "get_farm_state",
                "description": "Read the latest game status from status.json.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_memory",
                "description": "Search for historical memories using a query.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The search query."},
                        "user_id": {"type": "string", "description": "The user ID."}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_wiki_info",
                "description": "Fetch Wiki knowledge using a path-like string (e.g., 'crops/parsnip').",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "The wiki path (summary, category, or category/topic)."}
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "execute_action",
                "description": "Execute a game action by writing it to commands.json.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action_json": {"type": "string", "description": "The JSON string of the action."}
                    },
                    "required": ["action_json"]
                }
            },
            {
                "name": "update_tactics",
                "description": "Update tactics configuration in tactics.json.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "config_json": {"type": "string", "description": "The JSON string of the configuration."}
                    },
                    "required": ["config_json"]
                }
            }
        ]

        self.system_prompt = """
You are an expert Stardew Valley AI Assistant. Your goal is to help the player optimize their farm and gameplay.
You have access to MCP tools to interact with the game state, memory, and wiki.

Strategic Planning Process:
1. Call `get_farm_state` to understand the current situation (energy, money, inventory, crops).
2. (Optional) Call `get_wiki_info` for optimal strategies if you are unsure about a crop or NPC.
3. (Optional) Call `get_memory` to recall past player preferences or important events.
4. Analyze the visual screenshot (if provided) to identify things not in the JSON state.
5. Call `execute_action` to perform the chosen action.
6. (Optional) Call `update_tactics` if you need to adjust long-term behavior.

Instructions:
- Be autonomous. If you need more data, use the tools.
- Provide a clear rationale before executing actions.
- Use your vision to identify objects precisely.
"""

    def get_media_type(self, file_path):
        """Determine media type from file extension."""
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.png':
            return 'image/png'
        elif ext in ['.jpg', '.jpeg']:
            return 'image/jpeg'
        elif ext == '.gif':
            return 'image/gif'
        elif ext == '.webp':
            return 'image/webp'
        return 'image/jpeg'

    def _encode_image(self, image_path):
        """Encode image and detect media type."""
        media_type = self.get_media_type(image_path)
        with open(image_path, "rb") as image_file:
            data = image_file.read()
            return base64.b64encode(data).decode('utf-8'), media_type

    def _call_tool(self, tool_name, args):
        """Helper to call local tool implementations."""
        if tool_name == "get_farm_state":
            return get_farm_state()
        elif tool_name == "get_memory":
            return get_memory(args.get("query"), args.get("user_id", "stardew_player_1"))
        elif tool_name == "get_wiki_info":
            return get_wiki_info(args.get("path"))
        elif tool_name == "execute_action":
            return execute_action(args.get("action_json"))
        elif tool_name == "update_tactics":
            return update_tactics(args.get("config_json"))
        else:
            return f"Error: Tool {tool_name} not found."

    def decide_action(self, image_path=None):
        """
        Decide on the next action. Now supports multi-turn tool use.
        """
        messages = [{"role": "system", "content": self.system_prompt}]
        
        user_content = []
        if image_path and os.path.exists(image_path):
            base64_image, media_type = self._encode_image(image_path)
            if self.provider == "openai":
                user_content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:{media_type};base64,{base64_image}"}
                })
            elif self.provider == "anthropic":
                user_content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": base64_image
                    }
                })
        
        user_content.append({"type": "text", "text": "Observe the situation and decide on the next tactical action. Use get_farm_state first if you don't have the current state."})
        messages.append({"role": "user", "content": user_content})

        return self._run_conversation(messages)

    def _run_conversation(self, messages, max_turns=5):
        """Handle the multi-turn conversation with tool usage."""
        for _ in range(max_turns):
            if self.provider == "openai":
                tools_openai = [{"type": "function", "function": t} for t in self.tools]
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools_openai,
                    tool_choice="auto"
                )
                message = response.choices[0].message
                messages.append(message)
                
                if not message.tool_calls:
                    return message.content
                
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)
                    result = self._call_tool(tool_name, args)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result)
                    })

            elif self.provider == "anthropic":
                tools_anthropic = []
                for t in self.tools:
                    tools_anthropic.append({
                        "name": t["name"],
                        "description": t["description"],
                        "input_schema": t["parameters"]
                    })
                
                # Filter out system message for messages parameter, use system parameter instead
                history = [m for m in messages if m["role"] != "system"]
                
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2048,
                    system=self.system_prompt,
                    tools=tools_anthropic,
                    messages=history
                )
                
                # Add assistant message to history
                assistant_msg = {"role": "assistant", "content": response.content}
                messages.append(assistant_msg)
                
                if response.stop_reason != "tool_use":
                    # Extract text from content
                    text_content = "".join([c.text for c in response.content if c.type == "text"])
                    return text_content
                
                # Process tool calls
                tool_results = []
                for content in response.content:
                    if content.type == "tool_use":
                        result = self._call_tool(content.name, content.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": content.id,
                            "content": str(result)
                        })
                
                if tool_results:
                    messages.append({"role": "user", "content": tool_results})

        return "Max tool turns reached."

    def review_day(self, daily_logs, user_id="stardew_player_1"):
        """
        Review the day's logs with LLM to extract lessons and optimize tactics.
        Uses tool call support to update tactics.json.
        """
        review_system_prompt = """
You are a strategic advisor for a Stardew Valley AI. 
Your goal is to perform a deep post-mortem analysis of the day's performance.

Tasks:
1. Analyze successes, failures, and missed opportunities from the logs.
2. Identify 1-3 critical 'lessons learned' that will help the agent improve in the future.
3. If the performance indicates that the current tactics are suboptimal, use the `update_tactics` tool to refine the configuration.
4. Summarize your findings and the changes you've made.

Use `get_memory` or `get_wiki_info` if you need context to make better strategic decisions.
"""
        review_prompt = f"Analyze the following daily logs and provide a comprehensive review:\n{json.dumps(daily_logs, indent=2)}"
        
        messages = [
            {"role": "system", "content": review_system_prompt},
            {"role": "user", "content": review_prompt}
        ]

        report = self._run_conversation(messages)

        # Store the final report as a summary memory
        self.memory_manager.add_memory(f"Daily Review Summary: {report}", user_id=user_id)
        return report

if __name__ == "__main__":
    # Quick test initialization
    agent = StardewAgent(provider="openai", api_key="sk-...")
    print("Agent initialized.")

