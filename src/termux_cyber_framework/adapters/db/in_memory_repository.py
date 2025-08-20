import uuid
from typing import Dict, List
from termux_cyber_framework.core.domain.models import Vulnerability
from termux_cyber_framework.core.use_cases.ports import ReportRepositoryPort
from termux_cyber_framework.core.domain.exceptions import VulnerabilityNotFoundError

class InMemoryReportRepository(ReportRepositoryPort):
    """
    An in-memory implementation of the ReportRepositoryPort.
    This is useful for testing or running the application without a database.
    """

    def __init__(self):
        self._reports: Dict[str, List[Vulnerability]] = {}

    def save_vulnerabilities(self, vulnerabilities: List[Vulnerability]) -> str:
        report_id = str(uuid.uuid4())
        self._reports[report_id] = vulnerabilities
        return report_id

    def get_vulnerabilities_by_report_id(self, report_id: str) -> List[Vulnerability]:
        if report_id not in self._reports:
            raise VulnerabilityNotFoundError(f"Report with ID '{report_id}' not found.")
        return self._reports[report_id]
