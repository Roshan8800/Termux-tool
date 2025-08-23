import shutil
from termux_cyber_framework.core.use_cases.ports import LoggerPort, LogLevel

class DependencyAuditorAgent:
    """
    An agent responsible for auditing the system environment for potential
    dependency conflicts.
    """
    def __init__(self, logger: LoggerPort):
        self.logger = logger
        self.findings = []

    def _check_python_versions(self):
        """Checks for the presence of both python2 and python3."""
        self.logger.log("Checking for Python version conflicts...", level=LogLevel.DEBUG)
        python2_path = shutil.which("python2")
        python3_path = shutil.which("python3")

        if python2_path and python3_path:
            message = (
                "Both python2 and python3 are installed on the system. "
                "This can lead to conflicts if tools depend on different versions. "
                "Please ensure the correct python version is used when running scripts."
            )
            self.findings.append({"level": "WARNING", "message": message})
            self.logger.log(message, level=LogLevel.WARNING)

    def run_audit(self) -> list:
        """
        Runs all dependency audit checks.

        Returns:
            A list of findings, where each finding is a dictionary.
        """
        self.logger.log("Starting dependency audit...", level=LogLevel.INFO)
        self.findings = [] # Reset findings for each run

        self._check_python_versions()

        if not self.findings:
            self.logger.log("No dependency issues found.", level=LogLevel.INFO)

        return self.findings
