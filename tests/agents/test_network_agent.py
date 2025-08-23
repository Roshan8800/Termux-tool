import unittest
from unittest.mock import patch, MagicMock
from termux_cyber_framework.agents.network_agent import NetworkAgent
from requests.exceptions import ConnectionError

class TestNetworkAgent(unittest.TestCase):
    def setUp(self):
        mock_logger = MagicMock()
        self.agent = NetworkAgent(logger=mock_logger)

    @patch('requests.get')
    def test_check_internet_connection_online(self, mock_requests_get):
        """
        Test that check_internet_connection returns True when online.
        """
        # Configure the mock to simulate a successful request
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response

        # Call the method
        result = self.agent.check_internet_connection()

        # Assertions
        self.assertTrue(result)
        mock_requests_get.assert_called_once_with("http://www.google.com", timeout=5)

    @patch('requests.get')
    def test_check_internet_connection_offline(self, mock_requests_get):
        """
        Test that check_internet_connection returns False when offline.
        """
        # Configure the mock to simulate a failed request (e.g., timeout)
        mock_requests_get.side_effect = ConnectionError("Failed to connect")

        # Call the method
        result = self.agent.check_internet_connection()

        # Assertions
        self.assertFalse(result)
        mock_requests_get.assert_called_once_with("http://www.google.com", timeout=5)

if __name__ == '__main__':
    unittest.main()
