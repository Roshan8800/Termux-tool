import requests
from termux_cyber_framework.core.use_cases.ports import LoggerPort, LogLevel, NetworkPort

class NetworkAgent(NetworkPort):
    """
    An agent responsible for monitoring network connectivity.
    """
    def __init__(self, logger: LoggerPort):
        self.logger = logger

    def check_internet_connection(self) -> bool:
        """
        Checks for an active internet connection by making a request to a reliable server.
        """
        try:
            # Use a timeout to avoid hanging indefinitely
            response = requests.get("http://www.google.com", timeout=5)
            # Raise an exception for bad status codes (4xx or 5xx)
            response.raise_for_status()
            self.logger.log("Internet connectivity check successful.", level=LogLevel.DEBUG)
            return True
        except requests.RequestException as e:
            self.logger.log(f"Internet connectivity check failed: {e}", level=LogLevel.WARNING)
            return False
