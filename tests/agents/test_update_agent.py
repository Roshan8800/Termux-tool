import unittest
from unittest.mock import patch, MagicMock, call
import subprocess
from termux_cyber_framework.agents.update_agent import UpdateAgent
from termux_cyber_framework.core.use_cases.ports import LogLevel, AuditLoggerPort

class TestUpdateAgent(unittest.TestCase):

    def setUp(self):
        self.mock_logger = MagicMock()
        self.mock_audit_logger = MagicMock(spec=AuditLoggerPort)
        self.agent = UpdateAgent(logger=self.mock_logger, audit_logger=self.mock_audit_logger)

    @patch('subprocess.run')
    def test_check_framework_update_no_update(self, mock_run):
        """Test check_framework_update when no update is available."""
        mock_run.side_effect = [
            MagicMock(stdout=""),
            MagicMock(stdout="local_hash\n"),
            MagicMock(stdout="local_hash\n")
        ]
        self.assertFalse(self.agent.check_framework_update())

    @patch('subprocess.run')
    def test_check_framework_update_available(self, mock_run):
        """Test check_framework_update when an update is available."""
        mock_run.side_effect = [
            MagicMock(stdout=""),
            MagicMock(stdout="local_hash\n"),
            MagicMock(stdout="remote_hash\n")
        ]
        self.assertTrue(self.agent.check_framework_update())

    @patch('subprocess.run')
    def test_apply_framework_update_success(self, mock_run):
        """Test apply_framework_update logs success to audit log."""
        mock_run.return_value = MagicMock(stdout="success")
        with patch.object(self.agent, '_get_current_commit', side_effect=['before_hash', 'after_hash']):
            result = self.agent.apply_framework_update()
            self.assertTrue(result)
            self.mock_audit_logger.append.assert_called_once()
            self.assertEqual(self.mock_audit_logger.append.call_args[0][0]['status'], 'success')

    @patch('subprocess.run')
    def test_apply_framework_update_fails_and_rolls_back(self, mock_run):
        """Test apply_framework_update logs failure and rolls back."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "cmd", stderr="git pull error")
        with patch.object(self.agent, '_get_current_commit', return_value='before_hash'), \
             patch.object(self.agent, '_rollback_framework') as mock_rollback:

            result = self.agent.apply_framework_update()

            self.assertFalse(result)
            mock_rollback.assert_called_once_with('before_hash')
            self.mock_audit_logger.append.assert_called_once()
            self.assertEqual(self.mock_audit_logger.append.call_args[0][0]['status'], 'failure')

    # --- Tool Update Tests ---

    @patch('subprocess.run')
    def test_check_tool_updates_all_available(self, mock_run):
        """Test check_tool_updates when pkg and pip updates are available."""
        pip_output = "Package Version Latest\n---------- ------- -------\nrequests 2.25.1 2.26.0"
        mock_run.side_effect = [MagicMock(stdout=""), MagicMock(stdout=pip_output)]
        updates = self.agent.check_tool_updates()
        self.assertTrue(updates["pkg"])
        self.assertIn("requests", updates["pip"])

    @patch('subprocess.run')
    def test_apply_tool_updates_success(self, mock_run):
        """Test apply_tool_updates logs success to audit log."""
        mock_run.return_value = MagicMock(stdout="success")
        result = self.agent.apply_tool_updates(pip_packages=["requests"])
        self.assertTrue(result)
        self.assertEqual(self.mock_audit_logger.append.call_count, 2)
        self.assertEqual(self.mock_audit_logger.append.call_args_list[0][0][0]['component'], 'pkg')
        self.assertEqual(self.mock_audit_logger.append.call_args_list[0][0][0]['status'], 'success')
        self.assertEqual(self.mock_audit_logger.append.call_args_list[1][0][0]['component'], 'pip')
        self.assertEqual(self.mock_audit_logger.append.call_args_list[1][0][0]['status'], 'success')

    @patch('subprocess.run')
    def test_apply_tool_updates_pkg_fails(self, mock_run):
        """Test apply_tool_updates logs failure for pkg."""
        mock_run.side_effect = [subprocess.CalledProcessError(1, "cmd", stderr="pkg error"), MagicMock()]
        result = self.agent.apply_tool_updates(pip_packages=["requests"])
        self.assertFalse(result)
        self.mock_audit_logger.append.assert_any_call(unittest.mock.ANY)
        # Check the pkg failure log
        pkg_log = next(c[0][0] for c in self.mock_audit_logger.append.call_args_list if c[0][0]['component'] == 'pkg')
        self.assertEqual(pkg_log['status'], 'failure')

if __name__ == '__main__':
    unittest.main()
