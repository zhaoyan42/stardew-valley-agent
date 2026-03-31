import os
import json
import unittest
from unittest.mock import MagicMock, patch
from brain.mcp_server import get_farm_state, get_memory, get_wiki_info, execute_action, update_tactics
from brain.agent import StardewAgent

class TestAgentMCP(unittest.TestCase):
    def setUp(self):
        # Create dummy status.json
        self.dummy_status = {
            "player": {"name": "TestBot", "energy": 100, "money": 500},
            "location": "Farm",
            "crops": []
        }
        with open("status.json", "w", encoding='utf-8') as f:
            json.dump(self.dummy_status, f)

    def tearDown(self):
        # Clean up dummy files
        for f in ["status.json", "commands.json", "tactics.json"]:
            if os.path.exists(f):
                os.remove(f)

    def test_mcp_tools(self):
        # Test get_farm_state
        state = get_farm_state()
        self.assertIn("TestBot", state)
        
        # Test get_wiki_info (assuming data/wiki exists or handles error)
        wiki = get_wiki_info("summary")
        self.assertIsInstance(wiki, str)
        
        # Test execute_action
        action = {"action": "move", "target": "house"}
        res = execute_action(json.dumps(action))
        self.assertIn("successfully", res)
        with open("commands.json", "r") as f:
            self.assertEqual(json.load(f)["action"], "move")
            
        # Test update_tactics
        tactics = {"auto_water": True}
        res = update_tactics(json.dumps(tactics))
        self.assertIn("successfully", res)
        with open("tactics.json", "r") as f:
            self.assertEqual(json.load(f)["auto_water"], True)

    def test_agent_initialization(self):
        # Test agent can be initialized without crashing
        agent = StardewAgent(provider="openai", api_key="dummy_key")
        self.assertEqual(agent.provider, "openai")
        self.assertIn("Stardew Valley AI Assistant", agent.system_prompt)
        self.assertTrue(any(t["name"] == "get_farm_state" for t in agent.tools))

    @patch('brain.agent.OpenAI')
    def test_agent_review_day_tool_use(self, mock_openai):
        # Setup mock to simulate a tool call during review_day
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # 1st call: update_tactics tool call
        call1 = MagicMock()
        call1.choices = [MagicMock()]
        tool_call = MagicMock()
        tool_call.id = "call_rev_1"
        tool_call.function.name = "update_tactics"
        tool_call.function.arguments = json.dumps({"config_json": "{\"auto_water\": true}"})
        call1.choices[0].message.tool_calls = [tool_call]
        call1.choices[0].message.content = None
        
        # 2nd call: Final summary
        call2 = MagicMock()
        call2.choices = [MagicMock()]
        call2.choices[0].message.tool_calls = None
        call2.choices[0].message.content = "Review complete. Tactics updated to enable auto-watering."
        
        mock_client.chat.completions.create.side_effect = [call1, call2]
        
        agent = StardewAgent(provider="openai", api_key="dummy_key")
        logs = [{"action": "water", "status": "missed_some"}]
        report = agent.review_day(logs)
        
        self.assertIn("Review complete", report)
        self.assertEqual(mock_client.chat.completions.create.call_count, 2)
        # Verify tactics file was updated
        with open("tactics.json", "r") as f:
            data = json.load(f)
            self.assertEqual(data["auto_water"], True)

    @patch('brain.agent.OpenAI')
    def test_agent_decide_action_tool_use(self, mock_openai):
        # Setup mock to simulate one tool call and then a final response
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # 1st call: Tool call
        call1 = MagicMock()
        call1.choices = [MagicMock()]
        tool_call = MagicMock()
        tool_call.id = "call_123"
        tool_call.function.name = "get_farm_state"
        tool_call.function.arguments = "{}"
        call1.choices[0].message.tool_calls = [tool_call]
        call1.choices[0].message.content = None
        
        # 2nd call: Final answer
        call2 = MagicMock()
        call2.choices = [MagicMock()]
        call2.choices[0].message.tool_calls = None
        call2.choices[0].message.content = "I have checked the state and everything is fine."
        
        mock_client.chat.completions.create.side_effect = [call1, call2]
        
        agent = StardewAgent(provider="openai", api_key="dummy_key")
        result = agent.decide_action()
        
        self.assertEqual(result, "I have checked the state and everything is fine.")
        self.assertEqual(mock_client.chat.completions.create.call_count, 2)

    def test_multimodal_robustness(self):
        # Test get_media_type
        agent = StardewAgent(provider="openai", api_key="dummy_key")
        self.assertEqual(agent.get_media_type("test.png"), "image/png")
        self.assertEqual(agent.get_media_type("test.jpg"), "image/jpeg")
        self.assertEqual(agent.get_media_type("test.jpeg"), "image/jpeg")
        self.assertEqual(agent.get_media_type("test.webp"), "image/webp")
        self.assertEqual(agent.get_media_type("test.unknown"), "image/jpeg") # Default

        # Test _encode_image with a fake image
        with open("test.jpg", "wb") as f:
            # Minimal JPEG header
            f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF')
        
        base64_img, media_type = agent._encode_image("test.jpg")
        self.assertEqual(media_type, "image/jpeg")
        self.assertTrue(len(base64_img) > 0)
        
        os.remove("test.jpg")

if __name__ == "__main__":
    unittest.main()
