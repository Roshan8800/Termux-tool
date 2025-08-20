from termux_cyber_framework.core.domain.models import Report
from termux_cyber_framework.core.use_cases.ports import ReportGeneratorPort

class ConsoleReportGenerator(ReportGeneratorPort):
    """
    An adapter that generates and prints a report to the console.
    """
    def generate(self, report: Report) -> None:
        """
        Prints a formatted report to the standard output.

        Args:
            report: The report to be generated.
        """
        print("\n--- Execution Report ---")
        print(f"Command: '{report.command.raw_command}'")
        print(f"Success: {report.success}")

        if report.output:
            print("\n--- Output ---")
            print(report.output.strip())

        if report.error:
            print("\n--- Error ---")
            error_code = report.error.error_code
            print(f"Code: {error_code if error_code is not None else 'N/A'}")
            print(f"Message: {report.error.message.strip()}")

        print("----------------------")
