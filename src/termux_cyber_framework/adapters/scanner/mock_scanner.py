from typing import List
from termux_cyber_framework.core.domain.models import NetworkDevice, Vulnerability, Severity
from termux_cyber_framework.core.use_cases.ports import NetworkScannerPort

class MockNetworkScanner(NetworkScannerPort):
    """
    A mock implementation of the NetworkScannerPort.
    This adapter returns hardcoded data for demonstration and testing purposes.
    """

    def scan_network(self, ip_range: str) -> List[NetworkDevice]:
        print(f"[*] (Mock Scan) Scanning network for range: {ip_range}")
        # Return a couple of mock devices
        return [
            NetworkDevice(
                ip_address="192.168.1.1",
                mac_address="00:1A:2B:3C:4D:5E",
                hostname="router.local",
                open_ports=[80, 443]
            ),
            NetworkDevice(
                ip_address="192.168.1.101",
                mac_address="F6:E5:D4:C3:B2:A1",
                hostname="android-device.local",
                open_ports=[22, 8080]
            ),
        ]

    def scan_device_for_vulnerabilities(self, device: NetworkDevice) -> List[Vulnerability]:
        print(f"[*] (Mock Scan) Scanning device {device.ip_address} for vulnerabilities.")
        # Return a mock vulnerability for one of the devices
        if device.ip_address == "192.168.1.101":
            return [
                Vulnerability(
                    cve_id="CVE-2023-12345",
                    description="Mock vulnerability: Outdated SSH server allows remote code execution.",
                    severity=Severity.HIGH,
                    device=device
                )
            ]
        return []
