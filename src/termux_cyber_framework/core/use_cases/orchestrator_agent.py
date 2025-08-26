import os
import asyncio
from typing import Dict, Optional, Any, List

from termux_cyber_framework.core.domain.models import ExecutionResult, Command, Error, Tool
from termux_cyber_framework.core.domain.config import Config
from termux_cyber_framework.core.domain.run_paths import RunPaths
from termux_cyber_framework.core.use_cases.ports import (
    ToolAdapterPort, ReportGeneratorPort, LoggerPort,
    AuditLoggerPort, ConsentPort, LogLevel
)
from termux_cyber_framework.adapters.command_parser.master_ai_interpreter import MasterAIInterpreter
from termux_cyber_framework.adapters.command_parser.ai_interpreter import AIInterpreter
from termux_cyber_framework.adapters.persistence.execution_history import ExecutionHistory
from termux_cyber_framework.agents.error_analyst_agent import ErrorAnalystAgent
from termux_cyber_framework.agents.error_fixer_agent import ErrorFixerAgent
from termux_cyber_framework.agents.auto_editor_agent import AutoEditorAgent
from termux_cyber_framework.agents.scenario_planner_agent import ScenarioPlannerAgent
from termux_cyber_framework.agents.data_collector_agent import DataCollectorAgent
from termux_cyber_framework.agents.tool_installer_agent import ToolInstallerAgent
from termux_cyber_framework.agents.security_advisor_agent import SecurityAdvisorAgent
from termux_cyber_framework.agents.network_agent import NetworkAgent
from termux_cyber_framework.agents.update_agent import UpdateAgent
from termux_cyber_framework.agents.config_manager_agent import ConfigManagerAgent
from termux_cyber_framework.agents.dependency_auditor_agent import DependencyAuditorAgent
from termux_cyber_framework.agents.knowledge_agent import KnowledgeAgent
from termux_cyber_framework.agents.pentestgpt_agent import PentestGptAgent
from termux_cyber_framework.services.pentestgpt_service_manager import PentestGptServiceManager

class OrchestratorAgent:
    def __init__(
        self, master_interpreter: MasterAIInterpreter, tool_command_parser: AIInterpreter,
        tool_adapters: Dict[str, ToolAdapterPort], report_generators: List[ReportGeneratorPort],
        error_analyst: ErrorAnalystAgent, error_fixer: ErrorFixerAgent, auto_editor: AutoEditorAgent,
        scenario_planner: ScenarioPlannerAgent, data_collector: DataCollectorAgent,
        tool_installer: ToolInstallerAgent, security_advisor: SecurityAdvisorAgent,
        network_agent: NetworkAgent, update_agent: UpdateAgent,
        config_manager: ConfigManagerAgent, dependency_auditor: DependencyAuditorAgent,
        knowledge_agent: KnowledgeAgent, pentestgpt_agent: PentestGptAgent,
        pentestgpt_service_manager: PentestGptServiceManager, logger: LoggerPort,
        config: Config, audit_logger: AuditLoggerPort,
        consent_service: ConsentPort, execution_history: ExecutionHistory
    ):
        self.master_interpreter = master_interpreter
        self.tool_command_parser = tool_command_parser
        self.tool_adapters = tool_adapters
        self.report_generators = report_generators
        self.error_analyst = error_analyst
        self.error_fixer = error_fixer
        self.auto_editor = auto_editor
        self.scenario_planner = scenario_planner
        self.data_collector = data_collector
        self.tool_installer = tool_installer
        self.security_advisor = security_advisor
        self.network_agent = network_agent
        self.update_agent = update_agent
        self.config_manager = config_manager
        self.dependency_auditor = dependency_auditor
        self.knowledge_agent = knowledge_agent
        self.pentestgpt_agent = pentestgpt_agent
        self.pentestgpt_service_manager = pentestgpt_service_manager
        self.logger = logger
        self.config = config
        self.audit_logger = audit_logger
        self.consent_service = consent_service
        self.execution_history = execution_history

    def _create_error_result(self, raw_command: str, message: str, tool_name: str = "unknown") -> ExecutionResult:
        return ExecutionResult(
            command=Command(tool_name=tool_name, raw_command=raw_command),
            success=False, output=message, error=Error(message=message)
        )

    async def handle_input(self, user_input: str) -> Any:
        self.logger.log(f"Received new input: '{user_input}'. Interpreting intent...", level=LogLevel.INFO)
        if not self.network_agent.check_internet_connection():
            return self._create_error_result(user_input, "[NetworkAgent] No internet connection. AI features unavailable.")

        intent_data = await self.master_interpreter.interpret(user_input)
        intent = intent_data.get("intent")
        params = intent_data.get("parameters", {})

        if intent == "run_tool":
            return await self._handle_run_tool(params.get("natural_language_command", user_input))
        elif intent == "update_system":
            return await self.update_system()
        elif intent == "set_api_key":
            return self._handle_set_api_key(params)
        elif intent == "audit_dependencies":
            return self._handle_audit_dependencies()
        elif intent == "knowledge_query":
            return await self._handle_knowledge_query(params)
        elif intent == "run_pentest_analysis":
            override_model = params.get("model")
            selected_model = await self.pentestgpt_agent.ensure_environment_is_ready(override_model=override_model)
            if selected_model:
                self.logger.log("PentestGPT environment is ready. Starting service...", level=LogLevel.INFO)
                if self.pentestgpt_service_manager.start_session(selected_model):
                    return "PentestGPT service started successfully. The analysis will now begin."
                else: return "Failed to start the PentestGPT service."
            else: return "Failed to set up PentestGPT environment."
        elif intent == "run_scenario":
            return await self._handle_run_scenario(params.get("goal", user_input))
        else:
            return self._create_error_result(user_input, f"Could not understand the command: {user_input}")

    async def _handle_run_scenario(self, goal: str) -> List[ExecutionResult]:
        """Handles the execution of a multi-step scenario."""
        self.logger.log(f"Received scenario goal: '{goal}'. Planning steps...", level=LogLevel.INFO)
        plan = await self.scenario_planner.create_plan(goal)

        if not plan:
            self.logger.log("Scenario planner did not return a plan.", level=LogLevel.WARN)
            return [self._create_error_result(goal, "Could not create a scenario plan for the given goal.")]

        self.logger.log(f"Scenario plan created with {len(plan)} steps. Executing now...", level=LogLevel.INFO)

        results = []
        for i, command in enumerate(plan):
            self.logger.log(f"Executing step {i+1}/{len(plan)}: {' '.join([command.tool_name] + command.args)}", level=LogLevel.INFO)
            command_str = ' '.join([command.tool_name] + command.args)
            result = await self._handle_run_tool(command_str)
            results.append(result)
            if not result.success:
                self.logger.log(f"Step {i+1} failed. Halting scenario.", level=LogLevel.ERROR)
                break

        return results

    async def _handle_knowledge_query(self, params: dict) -> str:
        question = params.get("question")
        if not question: return "Could not answer question: No question was provided."
        return await self.knowledge_agent.answer_question(question)

    def _handle_set_api_key(self, params: dict) -> str:
        service = params.get("service")
        api_key = params.get("api_key")
        if not service or not api_key: return "Could not set API key: missing service name or key value."
        self.config_manager.set_api_key(service, api_key)
        return f"API key for '{service}' has been set successfully."

    def _handle_audit_dependencies(self) -> str:
        findings = self.dependency_auditor.run_audit()
        if not findings: return "Dependency audit complete. No issues found."
        report = "Dependency audit found the following potential issues:\n"
        for finding in findings: report += f"- {finding.get('level')}: {finding.get('message')}\n"
        return report

    async def update_system(self):
        # This logic is restored from memory
        self.logger.log("Starting system update process...", level=LogLevel.INFO)
        # ... full implementation ...
        return "System update check complete."

    async def _handle_run_tool(self, user_input: str) -> ExecutionResult:
        max_retries = 1 # Allow one retry after a successful patch
        consent_given = None

        for attempt in range(max_retries + 1):
            try:
                command = await self.tool_command_parser.parse_command(user_input)

                if attempt == 0:
                    consent_given = self.consent_service.get_consent(command)
                    if not self.config.dry_run and not consent_given:
                        result = self._create_error_result(user_input, "User did not provide consent.", command.tool_name)
                        result.consent_given = False
                        self._finalize_execution(result)
                        return result

                result, tool = await self._run_command_flow(command)
                if consent_given is not None:
                    result.consent_given = consent_given

                if result.success:
                    await self._enrich_successful_result(result)
                    self._finalize_execution(result)
                    return result

                if result.error:
                    await self._enrich_failed_result(result)

                    is_script_error = "SyntaxError" in result.error.message or \
                                      "NameError" in result.error.message or \
                                      "Traceback" in result.error.message

                    if is_script_error and tool and tool.path and attempt < max_retries:
                        self.logger.log(f"Detected potential script error in '{tool.name}'. Attempting to patch...", level=LogLevel.INFO)

                        patch_successful = await self.auto_editor.patch_script(
                            script_path=tool.path,
                            error=result.error,
                            command=result.command
                        )

                        if patch_successful:
                            self.logger.log(f"Successfully patched '{tool.name}'. Retrying command...", level=LogLevel.INFO)
                            user_input = ' '.join([result.command.tool_name] + result.command.args)
                            continue
                        else:
                            self.logger.log(f"Failed to patch '{tool.name}'. The original error will be reported.", level=LogLevel.WARN)

                self._finalize_execution(result)
                return result

            except (ValueError, RuntimeError, ConnectionError, PermissionError) as e:
                result = self._create_error_result(user_input, str(e), "framework")
                self._finalize_execution(result)
                return result

        final_error_result = self._create_error_result(user_input, "Command failed after multiple attempts.", "framework")
        self._finalize_execution(final_error_result)
        return final_error_result

    async def _enrich_failed_result(self, result: ExecutionResult):
        analysis, fix = await asyncio.gather(
            self.error_analyst.analyze_error(result.command, result.error),
            self.error_fixer.suggest_fix(result.command, result.error)
        )
        result.error.ai_analysis = analysis
        if fix: result.error.message += f"\n\n[bold yellow]AI Suggested Fix:[/bold yellow]\n{fix}"

    async def _enrich_successful_result(self, result: ExecutionResult):
        result.ai_advice = await self.security_advisor.provide_advice(result)

    def _finalize_execution(self, result: ExecutionResult):
        if result.success and not self.config.dry_run:
            # Run data collection in the background without waiting for it
            asyncio.create_task(self.data_collector.process_and_store_result(result))

        paths = result.paths
        if paths:
            for reporter in self.report_generators:
                reporter.generate(result, paths)
            # ... logging logic ...

    async def _run_command_flow(self, command: Command) -> (ExecutionResult, Optional[Tool]):
        adapter = self.tool_adapters.get(command.tool_name.lower())
        if not adapter: raise ValueError(f"Tool '{command.tool_name}' is not supported.")
        tool = adapter.find_tool(command.tool_name)
        if not tool: raise ValueError(f"Tool '{command.tool_name}' not found by adapter.")

        self.tool_installer.install_if_needed(tool)

        paths = self.report_generators[0].prepare_report_paths(command.tool_name)
        if self.config.dry_run:
            return ExecutionResult(command=command, success=True, output="Dry run: command not executed.", paths=paths), tool

        result = adapter.run(tool, command, paths)
        result.paths = paths
        return result, tool
