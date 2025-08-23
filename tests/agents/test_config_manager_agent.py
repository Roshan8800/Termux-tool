import unittest
from unittest.mock import MagicMock
import json
from termux_cyber_framework.agents.config_manager_agent import ConfigManagerAgent
from termux_cyber_framework.agents.file_manager_agent import FileManagerAgent

class TestConfigManagerAgent(unittest.TestCase):

    def setUp(self):
        self.mock_file_manager = MagicMock(spec=FileManagerAgent)

    def test_get_api_key_exists(self):
        """Test retrieving an API key that exists in the config."""
        # Arrange
        mock_config = {"api_keys": {"google_gemini": "test_key_123"}}
        self.mock_file_manager.path_exists.return_value = True
        self.mock_file_manager.read_file.return_value = json.dumps(mock_config)

        agent = ConfigManagerAgent(file_manager=self.mock_file_manager)

        # Act
        key = agent.get_api_key("google_gemini")

        # Assert
        self.assertEqual(key, "test_key_123")

    def test_get_api_key_not_exists(self):
        """Test retrieving an API key that does not exist."""
        # Arrange
        mock_config = {"api_keys": {}}
        self.mock_file_manager.path_exists.return_value = True
        self.mock_file_manager.read_file.return_value = json.dumps(mock_config)

        agent = ConfigManagerAgent(file_manager=self.mock_file_manager)

        # Act
        key = agent.get_api_key("open_router")

        # Assert
        self.assertIsNone(key)

    def test_set_api_key_new(self):
        """Test setting a new API key."""
        # Arrange
        self.mock_file_manager.path_exists.return_value = True
        self.mock_file_manager.read_file.return_value = json.dumps({"api_keys": {}})
        self.mock_file_manager.write_file.return_value = True

        agent = ConfigManagerAgent(file_manager=self.mock_file_manager)

        # Act
        agent.set_api_key("google_gemini", "new_key_456")

        # Assert
        self.mock_file_manager.write_file.assert_called_once()
        written_content = self.mock_file_manager.write_file.call_args[0][1]
        written_data = json.loads(written_content)
        self.assertEqual(written_data["api_keys"]["google_gemini"], "new_key_456")

    def test_set_api_key_update_existing(self):
        """Test updating an existing API key."""
        # Arrange
        initial_config = {"api_keys": {"google_gemini": "old_key"}}
        self.mock_file_manager.path_exists.return_value = True
        self.mock_file_manager.read_file.return_value = json.dumps(initial_config)
        self.mock_file_manager.write_file.return_value = True

        agent = ConfigManagerAgent(file_manager=self.mock_file_manager)

        # Act
        agent.set_api_key("google_gemini", "updated_key_789")

        # Assert
        written_content = self.mock_file_manager.write_file.call_args[0][1]
        written_data = json.loads(written_content)
        self.assertEqual(written_data["api_keys"]["google_gemini"], "updated_key_789")

    def test_initialization_no_config_file(self):
        """Test that the agent initializes with a default config if the file is missing."""
        # Arrange
        self.mock_file_manager.path_exists.return_value = False

        agent = ConfigManagerAgent(file_manager=self.mock_file_manager)

        # Act & Assert
        self.assertEqual(agent.config, {"api_keys": {}})

if __name__ == '__main__':
    unittest.main()
