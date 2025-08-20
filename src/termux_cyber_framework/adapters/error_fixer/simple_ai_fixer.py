import copy
from typing import Optional
from termux_cyber_framework.core.domain.models import Command, Error
from termux_cyber_framework.core.use_cases.ports import ErrorFixerPort

class SimpleAiFixerAdapter(ErrorFixerPort):
    """
    A simple, rule-based implementation of the ErrorFixerPort.
    This serves as a placeholder for a more advanced AI model.
    """
    async def suggest_fix(self, error: Error, command: Command) -> Optional[Command]:
        """
        Suggests a fix based on simple string matching in the error message.
        """
        error_msg_lower = error.message.lower()

        # Rule 1: Handle generic "permission denied" or nmap's specific "must be root" error.
        if "permission denied" in error_msg_lower or "you must be root" in error_msg_lower:
            if command.tool_name != 'sudo':
                new_args = [command.tool_name] + command.args
                return Command(
                    tool_name="sudo",
                    args=new_args,
                    raw_command=f"sudo {command.raw_command}"
                )

        # Rule 2: Handle sqlmap's non-interactive error by suggesting '--batch'.
        if command.tool_name == "sqlmap" and "user input must be provided" in error_msg_lower:
            if "--batch" not in command.args:
                new_command = copy.deepcopy(command)
                new_command.args.append("--batch")
                new_command.raw_command += " --batch"
                return new_command

        # Rule 3: Handle "command not found" by suggesting installation.
        # This is a bit tricky as the fixer should return a runnable command.
        # For now, we will log this and return None, as installation is handled
        # before execution. This points to a misconfiguration in tools.json.
        if "command not found" in error_msg_lower:
            # In a more advanced system, this could trigger a re-installation
            # or a search for the correct package name.
            # For now, we just acknowledge it.
            print(f"[*] AI Fixer: '{command.tool_name}' not found. Check installation or 'tools.json' config.")


        return None # No suggestion found
