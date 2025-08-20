import asyncio
import typer
import os
from termux_cyber_framework.core.use_cases.run_tool_use_case import RunToolUseCase
from termux_cyber_framework.adapters.command_parser.ai_parser import AICommandParserAdapter
from termux_cyber_framework.adapters.tool_installer.dynamic_tool_manager import DynamicToolManagerAdapter
from termux_cyber_framework.adapters.tool_runner.generic_tool_runner import GenericToolRunnerAdapter
from termux_cyber_framework.adapters.report_generator.file_report_generator import FileReportGenerator
from termux_cyber_framework.adapters.error_fixer.simple_ai_fixer import SimpleAiFixerAdapter
from termux_cyber_framework.adapters.logger.file_logger import FileLoggerAdapter

app = typer.Typer(
    name="tcf",
    help="A natural language-powered cybersecurity framework for Termux."
)

def build_use_case() -> RunToolUseCase:
    """
    Composition Root: Constructs and wires all adapters and use cases.
    """
    # --- Adapters Initialization ---

    base_dir = os.path.dirname(os.path.abspath(__file__))
    manifest_path = os.path.join(
        base_dir, "..", "tool_installer", "tools.json"
    )

    # The new dynamic manager for tools and adapters
    tool_manager = DynamicToolManagerAdapter(manifest_path)

    # The manager now dynamically loads the runners from the manifest
    tool_runners = tool_manager.load_tool_runners()

    # Other adapters
    parser = AICommandParserAdapter() # Use the new AI-based parser
    report_generator = FileReportGenerator() # Use the new file-based reporter
    error_fixer = SimpleAiFixerAdapter()
    fallback_runner = GenericToolRunnerAdapter()
    logger = FileLoggerAdapter() # Use the new file-based logger

    # --- Use Case Construction ---

    return RunToolUseCase(
        parser=parser,
        tool_installer=tool_manager,
        tool_runners=tool_runners,
        report_generator=report_generator,
        fallback_runner=fallback_runner,
        error_fixer=error_fixer,
        logger=logger # Inject the logger
    )

@app.command()
def run(
    command: str = typer.Argument(..., help="The command to run in natural language.")
):
    """
    Runs a command by parsing it, ensuring the tool is installed,
    and executing it using the best available runner.
    """
    use_case = build_use_case()

    async def main():
        await use_case.execute(command)

    asyncio.run(main())

if __name__ == "__main__":
    app()
