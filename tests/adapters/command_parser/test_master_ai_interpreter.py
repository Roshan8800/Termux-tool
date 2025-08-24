import unittest
import asyncio
import json
from unittest.mock import patch, MagicMock, AsyncMock
from termux_cyber_framework.adapters.command_parser.master_ai_interpreter import MasterAIInterpreter

class TestMasterAIInterpreter(unittest.TestCase):

    def setUp(self):
        # This setup will be used for tests that need a valid agent instance
        self.patcher_configure = patch('google.generativeai.configure')
        self.patcher_model = patch('google.generativeai.GenerativeModel')

        self.mock_configure = self.patcher_configure.start()
        self.mock_model_class = self.patcher_model.start()

        self.mock_model_instance = MagicMock()
        self.mock_model_class.return_value = self.mock_model_instance

    def tearDown(self):
        self.patcher_configure.stop()
        self.patcher_model.stop()

    def test_init_handles_no_api_key(self):
        """Test that the agent initializes with model=None if no API key."""
        agent = MasterAIInterpreter(api_key=None)
        self.assertIsNone(agent.model)

    @patch('google.generativeai.configure', side_effect=Exception("Invalid Key"))
    def test_init_handles_bad_api_key(self, mock_configure):
        """Test that the agent initializes with model=None if the key is invalid."""
        agent = MasterAIInterpreter(api_key="bad-key")
        self.assertIsNone(agent.model)

    def test_interpret_run_tool(self):
        """Test interpreting a 'run_tool' command."""
        # Arrange
        response_json = {
            "intent": "run_tool",
            "parameters": {"natural_language_command": "scan example.com"}
        }
        mock_response = MagicMock()
        mock_response.text = json.dumps(response_json)
        self.mock_model_instance.generate_content_async = AsyncMock(return_value=mock_response)

        agent = MasterAIInterpreter(api_key="fake-key")

        # Act
        result = asyncio.run(agent.interpret("scan example.com"))

        # Assert
        self.assertEqual(result, response_json)

    def test_interpret_set_api_key(self):
        """Test interpreting a 'set_api_key' command."""
        response_json = {
            "intent": "set_api_key",
            "parameters": {"service": "google_gemini", "api_key": "123"}
        }
        mock_response = MagicMock()
        mock_response.text = json.dumps(response_json)
        self.mock_model_instance.generate_content_async = AsyncMock(return_value=mock_response)

        agent = MasterAIInterpreter(api_key="fake-key")
        result = asyncio.run(agent.interpret("set key to 123"))
        self.assertEqual(result, response_json)

    def test_interpret_handles_invalid_json(self):
        """Test that the interpreter returns an error for invalid JSON."""
        mock_response = MagicMock()
        mock_response.text = "this is not json"
        self.mock_model_instance.generate_content_async = AsyncMock(return_value=mock_response)

        agent = MasterAIInterpreter(api_key="fake-key")
        result = asyncio.run(agent.interpret("some command"))

        self.assertEqual(result["intent"], "error")
        self.assertIn("Failed to interpret command", result["parameters"]["message"])

    def test_interpret_handles_api_error(self):
        """Test that the interpreter returns an error on API failure."""
        self.mock_model_instance.generate_content_async = AsyncMock(side_effect=Exception("API Error"))

        agent = MasterAIInterpreter(api_key="fake-key")
        result = asyncio.run(agent.interpret("some command"))

        self.assertEqual(result["intent"], "error")
        self.assertIn("API Error", result["parameters"]["message"])

if __name__ == '__main__':
    unittest.main()
