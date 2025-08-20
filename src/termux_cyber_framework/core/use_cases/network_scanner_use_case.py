from typing import List
from termux_cyber_framework.core.domain.models import Vulnerability
from termux_cyber_framework.core.use_cases.ports import NetworkScannerPort, ReportRepositoryPort

class NetworkScannerUseCase:
    """
    This use case orchestrates the process of scanning a network, checking for
    vulnerabilities, and saving the results.
    """

    def __init__(self, scanner: NetworkScannerPort, repository: ReportRepositoryPort):
        """
        Initializes the use case with the necessary adapters (via ports).

        Args:
            scanner: An implementation of the NetworkScannerPort.
            repository: An implementation of the ReportRepositoryPort.
        """
        self.scanner = scanner
        self.repository = repository

    def execute(self, ip_range: str) -> str:
        """
        Executes the network scan and vulnerability assessment.

        Args:
            ip_range: The IP range to scan.

        Returns:
            The ID of the generated report.
        """
        print(f"[*] Starting network scan for IP range: {ip_range}")

        # 1. Scan the network to discover devices
        devices = self.scanner.scan_network(ip_range)
        if not devices:
            print("[-] No devices found on the network.")
            return "no_devices_found"

        print(f"[+] Found {len(devices)} device(s).")

        # 2. For each device, scan for vulnerabilities
        all_vulnerabilities: List[Vulnerability] = []
        for device in devices:
            print(f"[*] Scanning device {device.ip_address} for vulnerabilities...")
            vulnerabilities = self.scanner.scan_device_for_vulnerabilities(device)
            if vulnerabilities:
                print(f"[+] Found {len(vulnerabilities)} vulnerabilities on {device.ip_address}.")
                all_vulnerabilities.extend(vulnerabilities)
            else:
                print(f"[-] No vulnerabilities found on {device.ip_address}.")

        # 3. If any vulnerabilities were found, save them in a report
        if not all_vulnerabilities:
            print("[-] No vulnerabilities found across all devices.")
            return "no_vulnerabilities_found"

        print(f"[*] Saving {len(all_vulnerabilities)} found vulnerabilities...")
        report_id = self.repository.save_vulnerabilities(all_vulnerabilities)
        print(f"[+] Report saved with ID: {report_id}")

        return report_id
