import os

class InstallLogger:
    """
    A simple logger for installation processes.
    """
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def log(self, tool_name: str, content: str):
        """
        Logs the content to a tool-specific installation log file.
        """
        if content:
            log_file = os.path.join(self.log_dir, f"install-{tool_name}.log")
            with open(log_file, "a") as f:
                f.write(content + "\n")
