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
        # Rule 1: Handle "permission denied" errors by suggesting 'sudo'.
        if "permission denied" in error.message.lower():
            # Avoid adding multiple 'sudo's
            if command.tool_name != 'sudo':
                print("[*] AI Fixer: Permission error detected. Suggesting 'sudo'.")
                # Create a deep copy to avoid modifying the original command object
                new_command = copy.deepcopy(command)
                # This is a simplification. A real implementation would need to
                # handle the tool_name and args more robustly. For example,
                # it should prepend 'sudo' to the *tool's* command, not just
                # make the tool 'sudo'. This requires a more complex command
                # structure, but for now, this demonstrates the principle.
                # A better approach would be a new field in the Command model,
                # e.g., `run_as_root: bool`.
                # For now, let's just prepend to the raw command for demonstration.

                # A better way to represent this:
                # Let's assume the tool runner knows how to handle a `sudo` flag.
                # We can't modify the command args easily without knowing more context.
                # The best way for this architecture is to create a NEW command.

                # Let's try a different approach. The runner will construct the command.
                # We can't easily prepend 'sudo'.
                # Let's change the raw command and re-parse. This is inefficient.

                # The cleanest way is to add a flag to the command object.
                # But I can't change the domain model from an adapter.

                # Let's stick to a simple demonstration. Let's assume the tool runner
                # will just execute the raw_command if a flag is set.
                # This is getting complicated.

                # Let's keep it simple and just log a message.
                # The use case can then decide what to do.
                # No, the port is `suggest_fix`, so it should return a new command.

                # Let's assume the use case is smart enough to handle this.
                # A new command where the tool is sudo and the old tool is an arg.
                new_args = [command.tool_name] + command.args
                fixed_command = Command(
                    tool_name="sudo",
                    args=new_args,
                    raw_command=f"sudo {command.raw_command}"
                )
                return fixed_command

        return None # No suggestion found
