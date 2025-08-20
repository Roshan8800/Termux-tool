import typer
from termux_cyber_framework.core.use_cases.network_scanner_use_case import NetworkScannerUseCase
from termux_cyber_framework.adapters.scanner.mock_scanner import MockNetworkScanner
from termux_cyber_framework.adapters.db.in_memory_repository import InMemoryReportRepository

# Create a Typer application
app = typer.Typer(
    name="termux-cyber-framework",
    help="An AI-powered cybersecurity framework for Termux."
)

def get_use_case() -> NetworkScannerUseCase:
    """
    This function acts as a simplified Dependency Injection container.
    It creates and wires up the necessary components. This is the
    "Composition Root" of the application.
    """
    # In a real application, you might read configuration here to decide
    # which adapters to use (e.g., MockScanner vs. NmapScanner).
    scanner_adapter = MockNetworkScanner()
    repository_adapter = InMemoryReportRepository()
    return NetworkScannerUseCase(scanner=scanner_adapter, repository=repository_adapter)

@app.command()
def scan(
    ip_range: str = typer.Argument(
        "192.168.1.0/24",
        help="The IP range to scan, e.g., '192.168.1.0/24'."
    )
):
    """
    Scan a network for devices and vulnerabilities.
    """
    print("Initializing scanner...")
    # Get the fully wired use case
    scanner_use_case = get_use_case()
    # Execute the use case
    report_id = scanner_use_case.execute(ip_range)
    print(f"Scan complete. Report ID: {report_id}")

if __name__ == "__main__":
    app()
