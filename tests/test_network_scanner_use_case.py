import pytest
from termux_cyber_framework.core.use_cases.network_scanner_use_case import NetworkScannerUseCase
from termux_cyber_framework.adapters.scanner.mock_scanner import MockNetworkScanner
from termux_cyber_framework.adapters.db.in_memory_repository import InMemoryReportRepository

def test_network_scanner_use_case_with_mocks():
    """
    Tests the full flow of the network scanner use case with mock adapters.
    """
    # Arrange: Set up the use case with mock implementations
    scanner = MockNetworkScanner()
    repository = InMemoryReportRepository()
    use_case = NetworkScannerUseCase(scanner, repository)

    # Act: Execute the use case
    ip_range = "192.168.1.0/24"
    report_id = use_case.execute(ip_range)

    # Assert: Check if the results are as expected
    assert report_id != "no_devices_found"
    assert report_id != "no_vulnerabilities_found"

    # Verify that the report was saved correctly
    saved_vulnerabilities = repository.get_vulnerabilities_by_report_id(report_id)
    assert len(saved_vulnerabilities) == 1
    vulnerability = saved_vulnerabilities[0]
    assert vulnerability.cve_id == "CVE-2023-12345"
    assert vulnerability.device.ip_address == "192.168.1.101"
