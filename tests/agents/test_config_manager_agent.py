import unittest
from unittest.mock import patch, mock_open
import json
import os
from termux_cyber_framework.agents.config_manager_agent import ConfigManagerAgent

class TestConfigManagerAgent(unittest.TestCase):

    @patch("os.path.exists", return_value=True)
    def test_get_api_key_exists(self, mock_exists):
        """Test retrieving an API key that exists in the config."""
        mock_config = {"api_keys": {"google_gemini": "test_key_123"}}
        m = mock_open(read_data=json.dumps(mock_config))
        with patch("builtins.open", m):
            agent = ConfigManagerAgent(config_path="dummy/path/config.json")
            key = agent.get_api_key("google_gemini")
            self.assertEqual(key, "test_key_123")

    @patch("os.path.exists", return_value=True)
    def test_get_api_key_not_exists(self, mock_exists):
        """Test retrieving an API key that does not exist."""
        mock_config = {"api_keys": {}}
        m = mock_open(read_data=json.dumps(mock_config))
        with patch("builtins.open", m):
            agent = ConfigManagerAgent(config_path="dummy/path/config.json")
            key = agent.get_api_key("open_router")
            self.assertIsNone(key)

    @patch("os.path.exists", return_value=True)
    def test_set_api_key_new(self, mock_exists):
        """Test setting a new API key."""
        # Arrange
        m = mock_open(read_data=json.dumps({"api_keys": {}}))
        with patch("builtins.open", m), \
             patch.object(ConfigManagerAgent, '_save_config') as mock_save:

            agent = ConfigManagerAgent(config_path="dummy/path/config.json")

            # Act
            agent.set_api_key("google_gemini", "new_key_456")

            # Assert
            self.assertEqual(agent.config["api_keys"]["google_gemini"], "new_key_456")
            mock_save.assert_called_once()

    @patch("os.path.exists", return_value=True)
    def test_set_api_key_update_existing(self, mock_exists):
        """Test updating an existing API key."""
        # Arrange
        initial_config = {"api_keys": {"google_gemini": "old_key"}}
        m = mock_open(read_data=json.dumps(initial_config))
        with patch("builtins.open", m), \
             patch.object(ConfigManagerAgent, '_save_config') as mock_save:

            agent = ConfigManagerAgent(config_path="dummy/path/config.json")

            # Act
            agent.set_api_key("google_gemini", "updated_key_789")

            # Assert
            self.assertEqual(agent.config["api_keys"]["google_gemini"], "updated_key_789")
            mock_save.assert_called_once()

    @patch("os.path.exists", return_value=False)
    def test_initialization_no_config_file(self, mock_exists):
        """Test that the agent initializes with a default config if the file is missing."""
        agent = ConfigManagerAgent(config_path="dummy/path/config.json")
        key = agent.get_api_key("google_gemini")
        self.assertIsNone(key)
        self.assertEqual(agent.config, {"api_keys": {}})

if __name__ == '__main__':
    unittest.main()
