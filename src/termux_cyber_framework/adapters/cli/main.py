import asyncio
import typer
import os
from termux_cyber_framework.core.use_cases.run_tool_use_case import RunToolUseCase
from termux_cyber_framework.adapters.command_parser.simple_parser import SimpleCommandParserAdapter
from termux_cyber_framework.adapters.tool_manager.local_tool_manager import LocalToolManagerAdapter
from termux_cyber_framework.adapters.tool_runner.shell_tool_runner import ShellToolRunnerAdapter

app = typer.Typer(
    name="tcf",
    help="A natural language-powered cybersecurity framework for Termux."
)

def build_use_case() -> RunToolUseCase:
    """
    Composition Root: Constructs and wires all adapters and use cases.
    """
    # Construct the absolute path to the tools.json manifest
    # This makes the path resolution independent of the current working directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    manifest_path = os.path.join(
        base_dir, "..", "tool_manager", "tools.json"
    )

    parser = SimpleCommandParserAdapter()
    tool_manager = LocalToolManagerAdapter(manifest_path)
    tool_runner = ShellToolRunnerAdapter()

    return RunToolUseCase(
        parser=parser,
        tool_manager=tool_manager,
        tool_runner=tool_runner
    )

@app.command()
def run(
    command: str = typer.Argument(..., help="The command to run in natural language.")
):
    """
    Runs a command by parsing it, ensuring the tool is installed,
    and executing it.
    """
    print(f"[*] Received command: '{command}'")
    use_case = build_use_case()

    async def main():
        report = await use_case.execute(command)

        print("\n--- Execution Report ---")
        print(f"Command: '{report.command.raw_command}'")
        print(f"Success: {report.success}")

        if report.output:
            print("\n--- Output ---")
            print(report.output)

        if report.error:
            print("\n--- Error ---")
            print(f"Code: {report.error.error_code if report.error.error_code is not None else 'N/A'}")
            print(f"Message: {report.error.message}")
        print("----------------------")

    asyncio.run(main())

if __name__ == "__main__":
    app()
