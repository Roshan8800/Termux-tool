import os
from datetime import datetime
from termux_cyber_framework.core.use_cases.ports import LoggerPort, LogLevel

class FileLoggerAdapter(LoggerPort):
    """
    An adapter that logs messages to a file in the 'logs' directory.
    """
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        # Define the log file path based on the current date
        self.log_file = os.path.join(self.log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")

    def log(self, message: str, level: LogLevel = LogLevel.INFO):
        """
        Writes a timestamped log message to the daily log file.

        Args:
            message: The message to log.
            level: The severity level of the message.
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level.value}] {message}\n"

        try:
            with open(self.log_file, 'a') as f:
                f.write(log_entry)
        except Exception as e:
            # If logging fails, print to stderr as a last resort
            print(f"Error writing to log file: {e}")
            print(log_entry)
