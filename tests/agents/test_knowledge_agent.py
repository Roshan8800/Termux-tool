import unittest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import json
from termux_cyber_framework.agents.knowledge_agent import KnowledgeAgent
from termux_cyber_framework.agents.file_manager_agent import FileManagerAgent
from termux_cyber_framework.core.use_cases.ports import LoggerPort

class TestKnowledgeAgent(unittest.TestCase):

    def setUp(self):
        self.mock_file_manager = MagicMock(spec=FileManagerAgent)
        self.mock_logger = MagicMock(spec=LoggerPort)
        # Mock a tool catalog for the agent to load
        mock_catalog = [{"name": "nmap"}, {"name": "sqlmap"}]
        # Default mock for read_file to return the catalog. Tests can override.
        self.mock_file_manager.read_file.return_value = json.dumps(mock_catalog)

    def test_init_raises_error_if_no_api_key(self):
        """Test that the agent raises a ValueError if no API key is provided."""
        with self.assertRaises(ValueError):
            KnowledgeAgent(api_key=None, file_manager=self.mock_file_manager, logger=self.mock_logger, tool_catalog_path="")
        with self.assertRaises(ValueError):
            KnowledgeAgent(api_key="", file_manager=self.mock_file_manager, logger=self.mock_logger, tool_catalog_path="")

    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    def test_query_uses_cache(self, mock_configure, mock_model):
        """Test that a second query for the same question hits the cache."""
        # Arrange
        self.mock_file_manager.read_file.side_effect = [
            json.dumps([{"name": "nmap"}]), # tool catalog
            json.dumps({"how do i use nmap?": "cached nmap answer"}) # knowledge cache
        ]
        agent = KnowledgeAgent(
            api_key="fake_key", file_manager=self.mock_file_manager,
            logger=self.mock_logger, tool_catalog_path=""
        )
        question = "how do i use nmap?"

        # Act
        result = asyncio.run(agent.query(question))

        # Assert
        self.assertEqual(result, "cached nmap answer")
        # The AI model should NOT have been called
        mock_model.return_value.generate_content_async.assert_not_called()
        self.mock_logger.log.assert_any_call("Returning cached response for question: 'how do i use nmap?'", level=unittest.mock.ANY)

    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    def test_query_saves_to_cache(self, mock_configure, mock_model):
        """Test that a new query's result is saved to the cache."""
        # Arrange
        mock_response = MagicMock()
        mock_response.text = "a fresh answer"
        mock_model.return_value.generate_content_async = AsyncMock(return_value=mock_response)

        # Start with an empty cache
        self.mock_file_manager.read_file.side_effect = [
            json.dumps([]), # tool catalog
            json.dumps({})  # empty knowledge cache
        ]

        agent = KnowledgeAgent(
            api_key="fake_key", file_manager=self.mock_file_manager,
            logger=self.mock_logger, tool_catalog_path=""
        )
        question = "what is xss?"

        # Act
        asyncio.run(agent.query(question))

        # Assert
        # Check that the file manager was called to save the cache
        self.mock_file_manager.write_file.assert_called_once()
        written_content = self.mock_file_manager.write_file.call_args[0][1]
        cache_data = json.loads(written_content)
        self.assertIn(question, cache_data)
        self.assertEqual(cache_data[question], "a fresh answer")

if __name__ == '__main__':
    unittest.main()
