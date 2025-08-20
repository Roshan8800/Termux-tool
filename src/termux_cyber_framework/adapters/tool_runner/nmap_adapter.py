import ipaddress
from .generic_runner import GenericRunner
from termux_cyber_framework.core.domain.models import Command, Tool, ExecutionResult
from termux_cyber_framework.core.domain.run_paths import RunPaths
from termux_cyber_framework.core.command_runner import CommandRunner

class NmapAdapter(GenericRunner):
    """
    A specific ToolRunnerPort implementation for the Nmap tool.
    """
    def __init__(self, command_runner: CommandRunner = None):
        super().__init__(command_runner)

    def _is_cidr(self, s: str) -> bool:
        try:
            ipaddress.ip_network(s, strict=False)
            return True
        except ValueError:
            return False

    def run(self, tool: Tool, command: Command, paths: RunPaths) -> ExecutionResult:
        args = command.args
        if "-T3" not in args:
            args.append("-T3")
        if "-sV" not in args:
            args.append("-sV")

        targets = [arg for arg in args if not arg.startswith("-")]
        non_targets = [arg for arg in args if arg.startswith("-")]

        if any(self._is_cidr(target) for target in targets):
            cidr_target = next(target for target in targets if self._is_cidr(target))
            network = ipaddress.ip_network(cidr_target)
            hosts = list(network.hosts())

            results = []
            for host in hosts:
                new_args = non_targets + [str(host)]
                new_command = Command(tool_name=command.tool_name, args=new_args, raw_command=f"{command.tool_name} {' '.join(new_args)}")
                result = super().run(tool, new_command, paths)
                results.append(result)

            if results:
                summary_output = "\n".join([r.output for r in results])
                summary_findings = []
                for r in results:
                    if r.findings:
                        summary_findings.extend(r.findings)

                return ExecutionResult(
                    command=command,
                    success=all(r.success for r in results),
                    output=summary_output,
                    error=results[-1].error if not all(r.success for r in results) else None,
                    start_time=results[0].start_time,
                    end_time=results[-1].end_time,
                    findings=summary_findings
                )

        return super().run(tool, command, paths)
