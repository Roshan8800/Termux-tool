import unittest
from unittest.mock import patch, MagicMock, mock_open, call
import json
from termux_cyber_framework.agents.doctor_agent import DoctorAgent
from termux_cyber_framework.core.use_cases.ports import LogLevel

class TestDoctorAgent(unittest.TestCase):

    def setUp(self):
        self.mock_logger = MagicMock()
        self.config_paths = ['config/config.json', 'data/tool_catalog.json']
        self.tool_catalog_path = 'data/tool_catalog.json'
        self.doctor = DoctorAgent(
            logger=self.mock_logger,
            config_paths=self.config_paths,
            tool_catalog_path=self.tool_catalog_path
        )

    @patch('shutil.copy')
    @patch('shutil.which', return_value='/usr/bin/nmap')
    @patch('os.getenv', return_value='fake_api_key')
    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps({"tools": [{"name": "nmap", "run_command": "nmap"}]}))
    @patch('os.path.exists', return_value=True)
    def test_run_checks_all_ok_and_backup(self, mock_exists, mock_open, mock_getenv, mock_which, mock_copy):
        """Test that run_checks completes and calls backup when all is well."""
        # Act
        self.doctor.run_checks()

        # Assert
        self.mock_logger.log.assert_any_call("System health checks passed successfully.", level=LogLevel.INFO)

        # Check that backup was called for each config file
        expected_backup_calls = [
            call('config/config.json', 'config/config.json.bak'),
            call('data/tool_catalog.json', 'data/tool_catalog.json.bak')
        ]
        mock_copy.assert_has_calls(expected_backup_calls, any_order=True)

    @patch('shutil.copy')
    def test_restore_from_backup_success(self, mock_copy):
        """Test that a missing file triggers a successful restore from backup."""
        # Arrange
        # Side effect for os.path.exists:
        # 1. First check for config.json -> False (missing)
        # 2. Check for config.json.bak -> True (backup exists)
        # 3. Second check for config.json after restore -> True
        # 4. Check for data/tool_catalog.json -> True
        mock_exists = MagicMock(side_effect=[False, True, True, True])

        # Side effect for open:
        # The first open will be the restore, then the successful reads
        m_open = mock_open(read_data=json.dumps({}))

        with patch('os.path.exists', mock_exists), patch('builtins.open', m_open):
            # Act
            self.doctor.run_checks()

            # Assert
            mock_copy.assert_any_call('config/config.json.bak', 'config/config.json')
            self.mock_logger.log.assert_any_call("Successfully restored 'config/config.json'.", level=LogLevel.INFO)
            self.mock_logger.log.assert_any_call("System health checks passed successfully.", level=LogLevel.INFO)

    @patch('shutil.copy')
    def test_restore_fails_when_backup_is_missing(self, mock_copy):
        """Test that run_checks fails if a file is missing and its backup is also missing."""
        # Side effect for os.path.exists:
        # 1. Check for config.json -> False (missing)
        # 2. Check for config.json.bak -> False (backup also missing)
        mock_exists = MagicMock(side_effect=[False, False])

        with patch('os.path.exists', mock_exists):
            with self.assertRaises(ValueError):
                self.doctor.run_checks()

            # Assert that restore was attempted but failed
            self.mock_logger.log.assert_any_call("Backup file 'config/config.json.bak' not found. Cannot restore.", level=LogLevel.ERROR)
            mock_copy.assert_not_called()

    def test_restore_fails_when_backup_is_corrupt(self):
        """Test that run_checks fails if the restored file is also corrupt."""
        # Side effect for os.path.exists: always true
        mock_exists = MagicMock(return_value=True)

        # Side effect for json.load: first it fails, then the restored one also fails
        mock_json_load = MagicMock(side_effect=[json.JSONDecodeError("err", "doc", 0), json.JSONDecodeError("err", "doc", 0)])

        with patch('os.path.exists', mock_exists), \
             patch('builtins.open', mock_open(read_data="corrupt")), \
             patch('json.load', mock_json_load), \
             patch('shutil.copy'):

            with self.assertRaises(ValueError):
                self.doctor.run_checks()

            # Assert that restore was attempted
            self.mock_logger.log.assert_any_call("Successfully restored 'config/config.json'.", level=LogLevel.INFO)
            self.mock_logger.log.assert_any_call("A critical health check failed and could not be resolved: Critical configuration file 'config/config.json' is corrupt or missing and could not be restored.", level=LogLevel.ERROR)

    def test_check_api_key_missing_logs_warning(self):
        """Test that a warning is logged when the GOOGLE_API_KEY is not set."""
        with patch.object(self.doctor, '_check_config_integrity'), \
             patch.object(self.doctor, '_check_tool_availability'), \
             patch('os.getenv', return_value=None):

            self.doctor._check_api_key()

            self.mock_logger.log.assert_any_call(
                "GOOGLE_API_KEY environment variable is not set. AI features will be unavailable.",
                level=LogLevel.WARNING
            )

    def test_check_tool_availability_missing_logs_warning(self):
        """Test that a warning is logged for a missing tool."""
        mock_tool_catalog = {"tools": [{"name": "missingtool", "run_command": "missingtool"}]}

        with patch('builtins.open', mock_open(read_data=json.dumps(mock_tool_catalog))), \
             patch('shutil.which', return_value=None):

            self.doctor._check_tool_availability()

            self.mock_logger.log.assert_any_call(
                "The following tools are not on the PATH and may need installation: missingtool.",
                level=LogLevel.WARNING
            )

if __name__ == '__main__':
    unittest.main()
