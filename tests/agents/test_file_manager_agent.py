import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
import os
from termux_cyber_framework.agents.file_manager_agent import FileManagerAgent
from termux_cyber_framework.core.use_cases.ports import LogLevel

class TestFileManagerAgent(unittest.TestCase):

    def setUp(self):
        self.mock_logger = MagicMock()
        self.agent = FileManagerAgent(logger=self.mock_logger)

    @patch('builtins.open', new_callable=mock_open, read_data="file content")
    def test_read_file_success(self, m_open):
        """Test read_file successfully reads content."""
        content = self.agent.read_file("dummy/path.txt")
        self.assertEqual(content, "file content")
        m_open.assert_called_once_with("dummy/path.txt", 'r')

    @patch('builtins.open', side_effect=IOError("Permission denied"))
    def test_read_file_failure(self, m_open):
        """Test read_file returns None and logs on failure."""
        content = self.agent.read_file("dummy/path.txt")
        self.assertIsNone(content)
        self.mock_logger.log.assert_any_call("Error reading file dummy/path.txt: Permission denied", level=LogLevel.ERROR)

    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_write_file_success(self, m_open, mock_makedirs):
        """Test write_file successfully writes content."""
        result = self.agent.write_file("dummy/path.txt", "new content")
        self.assertTrue(result)
        dir_path = os.path.dirname("dummy/path.txt")
        mock_makedirs.assert_called_once_with(dir_path, exist_ok=True)
        m_open.assert_called_once_with("dummy/path.txt", 'w')
        m_open().write.assert_called_once_with("new content")

    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_append_file_success(self, m_open, mock_makedirs):
        """Test append_file successfully appends content."""
        result = self.agent.append_file("dummy/path.txt", "appended content")
        self.assertTrue(result)
        dir_path = os.path.dirname("dummy/path.txt")
        mock_makedirs.assert_called_once_with(dir_path, exist_ok=True)
        m_open.assert_called_once_with("dummy/path.txt", 'a')
        m_open().write.assert_called_once_with("appended content")

    @patch('builtins.open', side_effect=IOError("Disk full"))
    def test_write_file_failure(self, m_open):
        """Test write_file returns False and logs on failure."""
        result = self.agent.write_file("dummy/path.txt", "new content")
        self.assertFalse(result)
        self.mock_logger.log.assert_any_call("Error writing to file dummy/path.txt: Disk full", level=LogLevel.ERROR)

    @patch('os.makedirs', return_value=None)
    def test_create_directory_success(self, mock_makedirs):
        """Test create_directory succeeds."""
        result = self.agent.create_directory("new/dir")
        self.assertTrue(result)
        mock_makedirs.assert_called_once_with("new/dir", exist_ok=True)

    @patch('shutil.copy')
    def test_copy_file_success(self, mock_copy):
        """Test copy_file succeeds."""
        result = self.agent.copy_file("a.txt", "b.txt")
        self.assertTrue(result)
        mock_copy.assert_called_once_with("a.txt", "b.txt")

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('os.remove')
    def test_delete_file_success(self, mock_remove, mock_isfile, mock_exists):
        """Test delete_file succeeds."""
        result = self.agent.delete_file("dummy.txt")
        self.assertTrue(result)
        mock_remove.assert_called_once_with("dummy.txt")

    @patch('os.path.isdir', return_value=True)
    @patch('shutil.rmtree')
    def test_delete_directory_success(self, mock_rmtree, mock_isdir):
        """Test delete_directory succeeds."""
        result = self.agent.delete_directory("dummy_dir")
        self.assertTrue(result)
        mock_rmtree.assert_called_once_with("dummy_dir")

    @patch('os.path.exists')
    def test_path_exists(self, mock_exists):
        """Test path_exists returns the correct boolean."""
        mock_exists.return_value = True
        self.assertTrue(self.agent.path_exists("a/path"))
        mock_exists.assert_called_once_with("a/path")

        mock_exists.return_value = False
        self.assertFalse(self.agent.path_exists("another/path"))

if __name__ == '__main__':
    unittest.main()
