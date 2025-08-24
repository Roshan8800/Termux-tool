import os
from termux_cyber_framework.core.domain.models import ExecutionResult
from termux_cyber_framework.core.domain.run_paths import RunPaths
from termux_cyber_framework.core.use_cases.ports import ReportGeneratorPort
from termux_cyber_framework.agents.file_manager_agent import FileManagerAgent

class MarkdownReporter(ReportGeneratorPort):
    """
    A report generator that creates reports in Markdown format.
    """
    def __init__(self, file_manager: FileManagerAgent):
        self._file_manager = file_manager

    def generate(self, result: ExecutionResult, paths: RunPaths) -> str:
        """
        Generates a Markdown report from an ExecutionResult.
        """
        report_path = os.path.join(paths.run_dir, f"{paths.base_filename}.md")

        content = []
        content.append(f"# Execution Report: `{result.command.raw_command}`")
        content.append(f"**Timestamp:** `{result.end_time.isoformat()}`")
        content.append("---")

        content.append("## Command Details")
        content.append(f"- **Tool:** `{result.command.tool_name}`")
        content.append(f"- **Arguments:** `{' '.join(result.command.args)}`")
        content.append(f"- **Consent Given:** `{result.consent_given}`")

        content.append("## Execution Summary")
        status = "Success" if result.success else "Failure"
        content.append(f"- **Status:** {status}")
        if result.error and result.error.error_code is not None:
            content.append(f"- **Exit Code:** `{result.error.error_code}`")

        if result.output:
            content.append("## Output")
            content.append(f"```\n{result.output.strip()}\n```")

        if not result.success and result.error:
            content.append("## Error Details")
            content.append(f"```\n{result.error.message.strip()}\n```")
            if result.error.ai_analysis:
                content.append("### AI Analysis")
                content.append(f"> {result.error.ai_analysis}")

        if result.ai_advice:
            content.append("## AI Security Advisor")
            content.append(f"> {result.ai_advice}")

        report_content = "\n\n".join(content)
        self._file_manager.write_file(report_path, report_content)

        return report_path

    def prepare_report_paths(self, tool_name: str) -> RunPaths:
        """This method is handled by the primary reporter, not needed here."""
        pass
