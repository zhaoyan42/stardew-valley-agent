import unittest
from unittest.mock import patch
import os
import json
from brain.init_wizard import init_wizard

class TestInitWizard(unittest.TestCase):
    @patch('builtins.input')
    def test_init_wizard(self, mock_input):
        # Mock inputs
        mock_input.side_effect = [
            'openai',           # provider
            'sk-test-key',      # api_key
            '',                 # base_url
            'Abigail',          # spouse
            'Min-max profit',   # style
            'Perfection'        # goal
        ]
        
        env_path = ".env"
        if os.path.exists(env_path):
            os.remove(env_path)
            
        init_wizard()
        
        # Verify .env
        self.assertTrue(os.path.exists(env_path))
        with open(env_path, 'r') as f:
            content = f.read()
            self.assertIn("OPENAI_API_KEY=sk-test-key", content)
            self.assertIn("LLM_PROVIDER=openai", content)
            
        # Verify Mem0 (Implicitly check it doesn't crash)
        # In a real test we'd check the DB, but here we just want to see if it runs.

if __name__ == '__main__':
    unittest.main()
