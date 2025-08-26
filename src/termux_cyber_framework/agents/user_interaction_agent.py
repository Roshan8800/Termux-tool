from typing import Union, List, Optional, Any
import google.generativeai as genai
from rich.console import Console
from rich.panel import Panel

from termux_cyber_framework.core.domain.models import ExecutionResult, Error, Command

class UserInteractionAgent:
    """
    An agent dedicated to handling all user-facing communication,
    translating structured results into natural language.
    """
    def __init__(self, console: Console, api_key: Optional[str] = None):
        self.console = console
        self.model = None
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash-latest')

    async def present_result(self, result_object: Union[ExecutionResult, List[ExecutionResult], Error, str]):
        """
        Main entry point for presenting any result to the user.
        Routes the result object to the appropriate handler.
        """
        try:
            if not self.model:
                # If AI is disabled, always use the raw presenter
                self._present_raw_result(result_object)
                return

            if isinstance(result_object, list):
                await self._summarize_scenario(result_object)
            elif isinstance(result_object, ExecutionResult):
                if result_object.success:
                    await self._summarize_success(result_object)
                else:
                    await self._explain_error(result_object)
            elif isinstance(result_object, Error):
                 await self._explain_error(ExecutionResult(command=Command(tool_name="framework", raw_command=""), success=False, error=result_object))
            elif isinstance(result_object, str):
                self.console.print(Panel(result_object, title="[bold blue]Info[/bold blue]", expand=False))
            else:
                self._present_raw_result(str(result_object))

        except Exception:
            # Graceful fallback for any failure in the AI summarization logic
            self.console.print(Panel("[bold yellow]AI summary failed. Showing raw output.[/bold yellow]", style="yellow", expand=False))
            self._present_raw_result(result_object)

    def _present_raw_result(self, result: Union[ExecutionResult, List[ExecutionResult], Any]):
        """
        Presents the raw, un-summarized result as a fallback.
        """
        if isinstance(result, list):
            self.console.print(Panel(f"Scenario with {len(result)} steps complete.", title="[bold blue]Scenario Report[/bold blue]", expand=False))
            for i, step_result in enumerate(result):
                command_str = ' '.join([step_result.command.tool_name] + step_result.command.args) if step_result.command else "N/A"
                self.console.print(f"--- Step {i+1}: {command_str} ---")
                self._present_raw_result(step_result)
            return

        if not isinstance(result, ExecutionResult):
            self.console.print(Panel(str(result), title="[bold yellow]Raw Output[/bold yellow]", expand=False))
            return

        title = "[bold green]Execution Succeeded[/bold green]"
        content = result.output
        if not result.success and result.error:
            title = "[bold red]Execution Failed[/bold red]"
            content = result.error.message
            if result.error.ai_analysis:
                content += f"\n\n[bold yellow]AI Analysis:[/bold yellow]\n{result.error.ai_analysis}"

        self.console.print(Panel(content, title=title, expand=False))

    async def _summarize_success(self, result: ExecutionResult):
        """Generates and prints a natural language summary for a successful execution."""
        prompt = f"""
You are a helpful cybersecurity assistant. A user has just successfully run a tool. Your task is to explain the results in a clear and simple way.

**Tool:**
"{result.command.tool_name}"

**Command Run:**
"{' '.join([result.command.tool_name] + result.command.args)}"

**Raw Output:**
```
{result.output}
```

**Your Task:**
1.  Briefly summarize the key findings from the output.
2.  Explain what the findings mean in a simple, accessible way.
3.  If applicable, suggest a logical next step the user could take.
"""
        response = await self.model.generate_content_async(prompt)
        self.console.print(Panel(response.text, title="[bold green]Summary[/bold green]", expand=False))

    async def _explain_error(self, result: ExecutionResult):
        """Generates and prints a natural language explanation for a failed execution."""
        prompt = f"""
You are a helpful cybersecurity assistant. A user's command has failed. Your task is to explain the error in a simple, non-technical way and offer clear advice.

**Command:**
"{' '.join([result.command.tool_name] + result.command.args) if result.command else 'N/A'}"

**Error Message:**
```
{result.error.message}
```

**AI Analysis (from ErrorAnalystAgent):**
```
{result.error.ai_analysis or 'No further analysis available.'}
```

**Your Task:**
1.  Explain to the user in simple terms why the command likely failed. Do not be overly technical.
2.  Based on the error and the AI analysis, suggest what the user should do next.
"""
        response = await self.model.generate_content_async(prompt)
        self.console.print(Panel(response.text, title="[bold red]Error Summary[/bold red]", expand=False))

    async def _summarize_scenario(self, results: List[ExecutionResult]):
        """Generates and prints a high-level summary for a multi-step scenario."""
        scenario_summary = []
        for i, result in enumerate(results):
            status = "Success" if result.success else "Failed"
            command_str = ' '.join([result.command.tool_name] + result.command.args) if result.command else "N/A"
            scenario_summary.append(f"Step {i+1}: `{command_str}` (Status: {status})")
            if not result.success:
                break

        summary_text = "\n".join(scenario_summary)

        prompt = f"""
You are a helpful cybersecurity assistant. A user has just completed a multi-step scenario. Your task is to provide a high-level summary of the outcome.

**Scenario Execution Summary:**
{summary_text}

**Your Task:**
1.  Briefly summarize what the scenario accomplished.
2.  If the scenario failed, explain at which step and why.
3.  Provide a concluding thought or suggest a high-level next course of action (e.g., "The initial reconnaissance is complete. You could now proceed to vulnerability scanning," or "The scenario failed at the Nmap step. You may need to fix the command before proceeding.").
"""
        response = await self.model.generate_content_async(prompt)
        self.console.print(Panel(response.text, title="[bold blue]Scenario Summary[/bold blue]", expand=False))
