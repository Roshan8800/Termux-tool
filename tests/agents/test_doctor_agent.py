import unittest
from unittest.mock import patch, MagicMock
import json
from termux_cyber_framework.agents.doctor_agent import DoctorAgent
from termux_cyber_framework.agents.config_manager_agent import ConfigManagerAgent
from termux_cyber_framework.agents.file_manager_agent import FileManagerAgent
from termux_cyber_framework.core.use_cases.ports import LogLevel

class TestDoctorAgent(unittest.TestCase):

    def setUp(self):
        self.mock_logger = MagicMock()
        self.mock_config_manager = MagicMock(spec=ConfigManagerAgent)
        self.mock_file_manager = MagicMock(spec=FileManagerAgent)
        self.config_paths = ['config/config.json']
        self.tool_catalog_path = 'data/tool_catalog.json'
        self.doctor = DoctorAgent(
            logger=self.mock_logger,
            config_manager=self.mock_config_manager,
            file_manager=self.mock_file_manager,
            config_paths=self.config_paths,
            tool_catalog_path=self.tool_catalog_path
        )

    def test_run_checks_all_ok(self):
        """Test run_checks completes successfully when all is well."""
        # Arrange
        self.mock_file_manager.read_file.return_value = json.dumps([{"name": "nmap", "run_command": "nmap"}])
        self.mock_file_manager.copy_file.return_value = True
        with patch('shutil.which', return_value='/usr/bin/nmap'), \
             patch('os.getenv', return_value='fake_api_key'):

            # Act
            self.doctor.run_checks()

            # Assert
            self.mock_logger.log.assert_any_call("System health checks passed successfully.", level=LogLevel.INFO)
            self.mock_file_manager.copy_file.assert_called_with('config/config.json', 'config/config.json.bak')

    def test_restore_from_backup_success(self):
        """Test that a missing file triggers a successful restore."""
        # Arrange
        # First read is None (missing), second is valid after restore
        self.mock_file_manager.read_file.side_effect = [None, json.dumps({})]
        self.mock_file_manager.path_exists.return_value = True # Backup exists
        self.mock_file_manager.copy_file.return_value = True

        # Act
        # We only test the integrity check part
        self.doctor._check_config_integrity()

        # Assert
        self.mock_file_manager.copy_file.assert_called_once_with('config/config.json.bak', 'config/config.json')
        self.mock_logger.log.assert_any_call("Successfully restored 'config/config.json'.", level=LogLevel.INFO)

    def test_restore_fails_when_backup_is_missing(self):
        """Test that run_checks fails if a file and its backup are missing."""
        self.mock_file_manager.read_file.return_value = None # File is missing/corrupt
        self.mock_file_manager.path_exists.return_value = False # Backup is missing

        with self.assertRaises(ValueError):
            self.doctor._check_config_integrity()

        self.mock_logger.log.assert_any_call("Backup file 'config/config.json.bak' not found. Cannot restore.", level=LogLevel.ERROR)
        self.mock_file_manager.copy_file.assert_not_called()

    def test_check_api_key_missing_logs_warning(self):
        """Test that a warning is logged when API key is in neither config nor env."""
        self.mock_config_manager.get_api_key.return_value = None
        with patch('os.getenv', return_value=None):
            self.doctor._check_api_key()
            self.mock_logger.log.assert_any_call(
                "Google API key is not set in config.json or as an environment variable. AI features will be unavailable.",
                level=LogLevel.WARNING
            )

    def test_check_tool_availability_missing_logs_warning(self):
        """Test that a warning is logged for a missing tool."""
        mock_tool_catalog = [{"name": "missingtool", "run_command": "missingtool"}]
        self.mock_file_manager.read_file.return_value = json.dumps(mock_tool_catalog)

        with patch('shutil.which', return_value=None):
            self.doctor._check_tool_availability()
            self.mock_logger.log.assert_any_call(
                "The following tools are not on the PATH and may need installation: missingtool.",
                level=LogLevel.WARNING
            )

if __name__ == '__main__':
    unittest.main()
