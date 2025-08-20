import asyncio
import typer
import os
from termux_cyber_framework.core.use_cases.run_tool_use_case import RunToolUseCase
from termux_cyber_framework.adapters.command_parser.simple_parser import SimpleCommandParserAdapter
from termux_cyber_framework.adapters.tool_installer.local_tool_installer import LocalToolInstallerAdapter
from termux_cyber_framework.adapters.tool_runner.generic_tool_runner import GenericToolRunnerAdapter
from termux_cyber_framework.adapters.tool_runner.nmap_adapter import NmapAdapter
from termux_cyber_framework.adapters.report_generator.console_report_generator import ConsoleReportGenerator
from termux_cyber_framework.adapters.error_fixer.simple_ai_fixer import SimpleAiFixerAdapter

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

    parser = SimpleCommandParserAdapter()
    tool_installer = LocalToolInstallerAdapter(manifest_path)
    report_generator = ConsoleReportGenerator()
    error_fixer = SimpleAiFixerAdapter() # New adapter

    tool_runners = {
        "nmap": NmapAdapter()
    }

    fallback_runner = GenericToolRunnerAdapter()

    # --- Use Case Construction ---

    return RunToolUseCase(
        parser=parser,
        tool_installer=tool_installer,
        tool_runners=tool_runners,
        report_generator=report_generator,
        fallback_runner=fallback_runner,
        error_fixer=error_fixer # New dependency
    )

@app.command()
def run(
    command: str = typer.Argument(..., help="The command to run in natural language.")
):
    """
    Runs a command by parsing it, ensuring the tool is installed,
    and executing it using the best available runner.
    """
    print(f"[*] Received command: '{command}'")
    use_case = build_use_case()

    async def main():
        await use_case.execute(command)

    asyncio.run(main())

if __name__ == "__main__":
    app()
