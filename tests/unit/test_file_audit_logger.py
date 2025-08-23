import unittest
from unittest.mock import MagicMock
import json
from termux_cyber_framework.adapters.audit_logger.file_audit_logger import FileAuditLogger
from termux_cyber_framework.agents.file_manager_agent import FileManagerAgent

class TestFileAuditLogger(unittest.TestCase):

    def setUp(self):
        self.mock_file_manager = MagicMock(spec=FileManagerAgent)

    def test_logger_initialization_creates_file(self):
        """Test that the logger creates the log file if it doesn't exist."""
        # Arrange
        self.mock_file_manager.path_exists.return_value = False

        # Act
        logger = FileAuditLogger(file_manager=self.mock_file_manager)

        # Assert
        self.mock_file_manager.write_file.assert_called_once_with(logger.log_path, "")

    def test_logger_initialization_does_not_create_file_if_exists(self):
        """Test that the logger does not create the log file if it already exists."""
        # Arrange
        self.mock_file_manager.path_exists.return_value = True

        # Act
        logger = FileAuditLogger(file_manager=self.mock_file_manager)

        # Assert
        self.mock_file_manager.write_file.assert_not_called()

    def test_append_writes_event_to_file(self):
        """Test that append calls the file manager's append_file method."""
        # Arrange
        self.mock_file_manager.path_exists.return_value = True
        logger = FileAuditLogger(file_manager=self.mock_file_manager)
        event = {"event": "test"}

        # Act
        logger.append(event)

        # Assert
        self.mock_file_manager.append_file.assert_called_once()
        # Check the content that was passed to append_file
        written_content = self.mock_file_manager.append_file.call_args[0][1]
        self.assertIn('"event": "test"', written_content)
        self.assertIn('"timestamp":', written_content)

if __name__ == '__main__':
    unittest.main()
