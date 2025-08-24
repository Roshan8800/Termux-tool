import os
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from termux_cyber_framework.core.domain.models import ExecutionResult
from termux_cyber_framework.core.domain.run_paths import RunPaths
from termux_cyber_framework.core.use_cases.ports import ReportGeneratorPort
from termux_cyber_framework.agents.file_manager_agent import FileManagerAgent

class PdfReporter(ReportGeneratorPort):
    """
    A report generator that creates reports in PDF format.
    """
    def __init__(self, file_manager: FileManagerAgent):
        self._file_manager = file_manager

    def generate(self, result: ExecutionResult, paths: RunPaths) -> str:
        """
        Generates a PDF report from an ExecutionResult.
        """
        report_path = os.path.join(paths.run_dir, f"{paths.base_filename}.pdf")

        pdf = FPDF()
        pdf.add_page()

        # Title
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, f"Execution Report: {result.command.raw_command}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        pdf.ln(5)

        # Metadata
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 5, f"Timestamp: {result.end_time.isoformat()}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
        pdf.ln(5)

        # Command Details
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "Command Details", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Courier", "", 10)
        pdf.multi_cell(0, 5, f"Tool: {result.command.tool_name}\nArgs: {' '.join(result.command.args)}")
        pdf.ln(5)

        # Execution Summary
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "Execution Summary", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", "", 10)
        status = "Success" if result.success else "Failure"
        pdf.cell(0, 5, f"Status: {status}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        if result.error and result.error.error_code is not None:
            pdf.cell(0, 5, f"Exit Code: {result.error.error_code}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(5)

        # Output
        if result.output:
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 10, "Output", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("Courier", "", 9)
            pdf.multi_cell(0, 5, result.output.strip())
            pdf.ln(5)

        # Error
        if not result.success and result.error:
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 10, "Error Details", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("Courier", "", 9)
            pdf.multi_cell(0, 5, result.error.message.strip())
            pdf.ln(5)
            if result.error.ai_analysis:
                pdf.set_font("Helvetica", "B", 10)
                pdf.cell(0, 10, "AI Analysis", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_font("Helvetica", "I", 10)
                pdf.multi_cell(0, 5, result.error.ai_analysis)
                pdf.ln(5)

        # AI Advisor
        if result.ai_advice:
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 10, "AI Security Advisor", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("Helvetica", "I", 10)
            pdf.multi_cell(0, 5, result.ai_advice)
            pdf.ln(5)

        pdf.output(report_path)

        return report_path

    def prepare_report_paths(self, tool_name: str) -> RunPaths:
        pass
