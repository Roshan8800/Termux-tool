import unittest
from unittest.mock import patch, MagicMock
from termux_cyber_framework.agents.dependency_auditor_agent import DependencyAuditorAgent

class TestDependencyAuditorAgent(unittest.TestCase):

    def setUp(self):
        self.mock_logger = MagicMock()
        self.agent = DependencyAuditorAgent(logger=self.mock_logger)

    @patch('shutil.which')
    def test_run_audit_finds_python_conflict(self, mock_which):
        """Test that a python2/python3 conflict is detected."""
        # Arrange
        # Simulate that both python2 and python3 are found on the PATH
        def which_side_effect(cmd):
            if cmd == "python2":
                return "/usr/bin/python2"
            if cmd == "python3":
                return "/usr/bin/python3"
            return None
        mock_which.side_effect = which_side_effect

        # Act
        findings = self.agent.run_audit()

        # Assert
        self.assertEqual(len(findings), 1)
        self.assertIn("Both python2 and python3 are installed", findings[0]['message'])

    @patch('shutil.which')
    def test_run_audit_no_conflict(self, mock_which):
        """Test that no conflict is detected when only python3 is present."""
        # Arrange
        def which_side_effect(cmd):
            if cmd == "python3":
                return "/usr/bin/python3"
            return None
        mock_which.side_effect = which_side_effect

        # Act
        findings = self.agent.run_audit()

        # Assert
        self.assertEqual(len(findings), 0)

    @patch('shutil.which', return_value=None)
    def test_run_audit_no_pythons(self, mock_which):
        """Test that no conflict is detected when neither python is present."""
        # Act
        findings = self.agent.run_audit()

        # Assert
        self.assertEqual(len(findings), 0)

if __name__ == '__main__':
    unittest.main()
