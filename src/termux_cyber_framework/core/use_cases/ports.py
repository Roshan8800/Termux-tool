from abc import ABC, abstractmethod
from typing import List
from termux_cyber_framework.core.domain.models import NetworkDevice, Vulnerability

class NetworkScannerPort(ABC):
    """
    A port for a network scanner. This defines the contract for any network
    scanning implementation that the core application will use.
    """

    @abstractmethod
    def scan_network(self, ip_range: str) -> List[NetworkDevice]:
        """
        Scans a given IP range and returns a list of discovered devices.

        Args:
            ip_range: The IP range to scan (e.g., '192.168.1.0/24').

        Returns:
            A list of NetworkDevice objects.
        """
        pass

    @abstractmethod
    def scan_device_for_vulnerabilities(self, device: NetworkDevice) -> List[Vulnerability]:
        """
        Scans a specific device for known vulnerabilities.

        Args:
            device: The NetworkDevice to scan.

        Returns:
            A list of Vulnerability objects found on the device.
        """
        pass


class ReportRepositoryPort(ABC):
    """
    A port for a report repository. This defines the contract for storing
    and retrieving scan reports.
    """

    @abstractmethod
    def save_vulnerabilities(self, vulnerabilities: List[Vulnerability]) -> str:
        """
        Saves a list of vulnerabilities to the repository.

        Args:
            vulnerabilities: A list of Vulnerability objects to save.

        Returns:
            A unique identifier for the saved report.
        """
        pass

    @abstractmethod
    def get_vulnerabilities_by_report_id(self, report_id: str) -> List[Vulnerability]:
        """
        Retrieves a list of vulnerabilities by its report ID.

        Args:
            report_id: The unique identifier of the report.

        Returns:
            A list of Vulnerability objects.
        """
        pass
