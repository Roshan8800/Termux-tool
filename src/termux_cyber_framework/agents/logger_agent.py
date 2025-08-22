from termux_cyber_framework.core.use_cases.ports import LoggerPort, LogLevel
from termux_cyber_framework.adapters.logger.file_logger import FileLoggerAdapter

class LoggerAgent(LoggerPort):
    """
    A dedicated agent for handling all logging activities in the framework.
    It encapsulates the underlying logging adapter.
    """
    def __init__(self):
        # In a more complex system, the adapter could be injected.
        # For now, we instantiate it directly.
        self._adapter = FileLoggerAdapter()

    def log(self, message: str, level: LogLevel = LogLevel.INFO):
        """
        Logs a message using the underlying adapter.
        """
        self._adapter.log(message, level)
