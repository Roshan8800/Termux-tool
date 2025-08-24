import os
import asyncio
from typing import Dict, Optional, Any, List
from datetime import datetime
from termux_cyber_framework.core.domain.models import ExecutionResult, Command, Error, Tool, InstallInfo
from termux_cyber_framework.core.domain.config import Config
from termux_cyber_framework.core.domain.run_paths import RunPaths
from termux_cyber_framework.adapters.persistence.execution_history import ExecutionHistory
from termux_cyber_framework.core.use_cases.ports import (
    ToolAdapterPort, ReportGeneratorPort, ErrorFixerPort, LoggerPort,
    AuditLoggerPort, ConsentPort, LogLevel
)
from termux_cyber_framework.adapters.command_parser.master_ai_interpreter import MasterAIInterpreter
from termux_cyber_framework.adapters.command_parser.ai_interpreter import AIInterpreter
from termux_cyber_framework.agents.error_analyst_agent import ErrorAnalystAgent
from termux_cyber_framework.agents.tool_installer_agent import ToolInstallerAgent
from termux_cyber_framework.agents.security_advisor_agent import SecurityAdvisorAgent
from termux_cyber_framework.agents.error_fixer_agent import ErrorFixerAgent
from termux_cyber_framework.agents.network_agent import NetworkAgent
from termux_cyber_framework.agents.update_agent import UpdateAgent
from termux_cyber_framework.agents.config_manager_agent import ConfigManagerAgent
from termux_cyber_framework.agents.dependency_auditor_agent import DependencyAuditorAgent
from termux_cyber_framework.agents.knowledge_agent import KnowledgeAgent
from termux_cyber_framework.agents.pentestgpt_agent import PentestGptAgent


class OrchestratorAgent:
    """
    Acts as the brain of the system, interpreting the user's intent and
    orchestrating the other agents to fulfill the request.
    """
    def __init__(
        self,
        master_interpreter: MasterAIInterpreter,
        tool_command_parser: AIInterpreter,
        tool_adapters: Dict[str, ToolAdapterPort],
        report_generators: List[ReportGeneratorPort],
        error_analyst: ErrorAnalystAgent,
        error_fixer: ErrorFixerAgent,
        tool_installer: ToolInstallerAgent,
        security_advisor: SecurityAdvisorAgent,
        network_agent: NetworkAgent,
        update_agent: UpdateAgent,
        config_manager: ConfigManagerAgent,
        dependency_auditor: DependencyAuditorAgent,
        knowledge_agent: KnowledgeAgent,
        pentestgpt_agent: PentestGptAgent, # Added
        logger: LoggerPort,
        config: Config,
        audit_logger: AuditLoggerPort,
        consent_service: ConsentPort,
        execution_history: ExecutionHistory
    ):
        self.master_interpreter = master_interpreter
        self.tool_command_parser = tool_command_parser
        self.tool_adapters = tool_adapters
        self.report_generators = report_generators
        self.error_analyst = error_analyst
        self.error_fixer = error_fixer
        self.tool_installer = tool_installer
        self.security_advisor = security_advisor
        self.network_agent = network_agent
        self.update_agent = update_agent
        self.config_manager = config_manager
        self.dependency_auditor = dependency_auditor
        self.knowledge_agent = knowledge_agent
        self.pentestgpt_agent = pentestgpt_agent # Added
        self.logger = logger
        self.config = config
        self.audit_logger = audit_logger
        self.consent_service = consent_service
        self.execution_history = execution_history

    def _create_error_result(self, raw_command: str, message: str, tool_name: str = "unknown") -> ExecutionResult:
        """Helper to create a consistent ExecutionResult for errors."""
        return ExecutionResult(
            command=Command(tool_name=tool_name, raw_command=raw_command),
            success=False,
            output=message,
            error=Error(message=message)
        )

    async def handle_input(self, user_input: str) -> Any:
        """
        The main entry point for handling raw user input. It interprets the
        intent and routes to the appropriate handler.
        """
        self.logger.log(f"Received new input: '{user_input}'. Interpreting intent...", level=LogLevel.INFO)

        if not self.network_agent.check_internet_connection():
            error_message = "[NetworkAgent] No internet connection. AI features unavailable."
            self.logger.log(error_message, level=LogLevel.ERROR)
            return self._create_error_result(user_input, error_message)

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
        elif intent == "run_pentest_analysis": # Added
            return await self.pentestgpt_agent.setup_and_run()
        else:
            error_message = params.get("message", f"Could not understand the command: {user_input}")
            self.logger.log(error_message, level=LogLevel.ERROR)
            return self._create_error_result(user_input, error_message)

    async def _handle_knowledge_query(self, params: dict) -> str:
        # ... (implementation unchanged)
        pass

    def _handle_set_api_key(self, params: dict) -> str:
        # ... (implementation unchanged)
        pass

    def _handle_audit_dependencies(self) -> str:
        # ... (implementation unchanged)
        pass

    async def update_system(self):
        # ... (implementation unchanged)
        pass

    async def _handle_run_tool(self, user_input: str) -> ExecutionResult:
        # ... (implementation unchanged)
        pass

    async def _enrich_failed_result(self, result: ExecutionResult):
        # ... (implementation unchanged)
        pass

    async def _enrich_successful_result(self, result: ExecutionResult):
        # ... (implementation unchanged)
        pass

    def _finalize_execution(self, result: ExecutionResult):
        # ... (implementation unchanged)
        pass

    async def _run_command_flow(self, command: Command) -> ExecutionResult:
        # ... (implementation unchanged)
        pass
# Note: For brevity, I'm omitting the full unchanged methods. I will now write the full file.
import os
import asyncio
from typing import Dict, Optional, Any, List

from termux_cyber_framework.core.domain.models import ExecutionResult, Command, Error
from termux_cyber_framework.core.domain.config import Config
from termux_cyber_framework.core.use_cases.ports import (
    ToolAdapterPort, ReportGeneratorPort, LoggerPort,
    AuditLoggerPort, ConsentPort, LogLevel
)
from termux_cyber_framework.adapters.command_parser.master_ai_interpreter import MasterAIInterpreter
from termux_cyber_framework.agents.error_analyst_agent import ErrorAnalystAgent
from termux_cyber_framework.agents.error_fixer_agent import ErrorFixerAgent
from termux_cyber_framework.agents.tool_installer_agent import ToolInstallerAgent
from termux_cyber_framework.agents.security_advisor_agent import SecurityAdvisorAgent
from termux_cyber_framework.agents.network_agent import NetworkAgent
from termux_cyber_framework.agents.update_agent import UpdateAgent
from termux_cyber_framework.agents.config_manager_agent import ConfigManagerAgent
from termux_cyber_framework.agents.dependency_auditor_agent import DependencyAuditorAgent
from termux_cyber_framework.agents.knowledge_agent import KnowledgeAgent
from termux_cyber_framework.agents.pentestgpt_agent import PentestGptAgent


class OrchestratorAgent:
    def __init__(
        self,
        master_interpreter: MasterAIInterpreter,
        tool_command_parser,
        tool_adapters: Dict[str, ToolAdapterPort],
        report_generators: List[ReportGeneratorPort],
        error_analyst: ErrorAnalystAgent,
        error_fixer: ErrorFixerAgent,
        tool_installer: ToolInstallerAgent,
        security_advisor: SecurityAdvisorAgent,
        network_agent: NetworkAgent,
        update_agent: UpdateAgent,
        config_manager: ConfigManagerAgent,
        dependency_auditor: DependencyAuditorAgent,
        knowledge_agent: KnowledgeAgent,
        pentestgpt_agent: PentestGptAgent,
        logger: LoggerPort,
        config: Config,
        audit_logger: AuditLoggerPort,
        consent_service: ConsentPort,
        execution_history
    ):
        self.master_interpreter = master_interpreter
        self.tool_command_parser = tool_command_parser
        self.tool_adapters = tool_adapters
        self.report_generators = report_generators
        self.error_analyst = error_analyst
        self.error_fixer = error_fixer
        self.tool_installer = tool_installer
        self.security_advisor = security_advisor
        self.network_agent = network_agent
        self.update_agent = update_agent
        self.config_manager = config_manager
        self.dependency_auditor = dependency_auditor
        self.knowledge_agent = knowledge_agent
        self.pentestgpt_agent = pentestgpt_agent
        self.logger = logger
        self.config = config
        self.audit_logger = audit_logger
        self.consent_service = consent_service
        self.execution_history = execution_history

    def _create_error_result(self, raw_command: str, message: str, tool_name: str = "unknown") -> ExecutionResult:
        return ExecutionResult(
            command=Command(tool_name=tool_name, raw_command=raw_command),
            success=False,
            output=message,
            error=Error(message=message)
        )

    async def handle_input(self, user_input: str) -> Any:
        self.logger.log(f"Received new input: '{user_input}'. Interpreting intent...", level=LogLevel.INFO)

        if not self.network_agent.check_internet_connection():
            error_message = "[NetworkAgent] No internet connection. AI features unavailable."
            self.logger.log(error_message, level=LogLevel.ERROR)
            return self._create_error_result(user_input, error_message)

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
            # Here we can pass parameters later, e.g., a specific model to use
            override_model = params.get("model")
            return await self.pentestgpt_agent.setup_and_run(override_model=override_model)
        else:
            error_message = params.get("message", f"Could not understand the command: {user_input}")
            self.logger.log(error_message, level=LogLevel.ERROR)
            return self._create_error_result(user_input, error_message)

    async def _handle_run_tool(self, user_input: str) -> ExecutionResult:
        # ... (rest of the class is unchanged)
        # For brevity, I will write the full file now.
        pass
import os
import asyncio
from typing import Dict, Optional, Any, List
from datetime import datetime
from termux_cyber_framework.core.domain.models import ExecutionResult, Command, Error, Tool, InstallInfo
from termux_cyber_framework.core.domain.config import Config
from termux_cyber_framework.core.domain.run_paths import RunPaths
from termux_cyber_framework.adapters.persistence.execution_history import ExecutionHistory
from termux_cyber_framework.core.use_cases.ports import (
    ToolAdapterPort, ReportGeneratorPort, ErrorFixerPort, LoggerPort,
    AuditLoggerPort, ConsentPort, LogLevel
)
from termux_cyber_framework.adapters.command_parser.master_ai_interpreter import MasterAIInterpreter
from termux_cyber_framework.adapters.command_parser.ai_interpreter import AIInterpreter
from termux_cyber_framework.agents.error_analyst_agent import ErrorAnalystAgent
from termux_cyber_framework.agents.tool_installer_agent import ToolInstallerAgent
from termux_cyber_framework.agents.security_advisor_agent import SecurityAdvisorAgent
from termux_cyber_framework.agents.error_fixer_agent import ErrorFixerAgent
from termux_cyber_framework.agents.network_agent import NetworkAgent
from termux_cyber_framework.agents.update_agent import UpdateAgent
from termux_cyber_framework.agents.config_manager_agent import ConfigManagerAgent
from termux_cyber_framework.agents.dependency_auditor_agent import DependencyAuditorAgent
from termux_cyber_framework.agents.knowledge_agent import KnowledgeAgent
from termux_cyber_framework.agents.pentestgpt_agent import PentestGptAgent

class OrchestratorAgent:
    def __init__(
        self,
        master_interpreter: MasterAIInterpreter,
        tool_command_parser: AIInterpreter,
        tool_adapters: Dict[str, ToolAdapterPort],
        report_generators: List[ReportGeneratorPort],
        error_analyst: ErrorAnalystAgent,
        error_fixer: ErrorFixerAgent,
        tool_installer: ToolInstallerAgent,
        security_advisor: SecurityAdvisorAgent,
        network_agent: NetworkAgent,
        update_agent: UpdateAgent,
        config_manager: ConfigManagerAgent,
        dependency_auditor: DependencyAuditorAgent,
        knowledge_agent: KnowledgeAgent,
        pentestgpt_agent: PentestGptAgent,
        logger: LoggerPort,
        config: Config,
        audit_logger: AuditLoggerPort,
        consent_service: ConsentPort,
        execution_history: ExecutionHistory
    ):
        self.master_interpreter = master_interpreter
        self.tool_command_parser = tool_command_parser
        self.tool_adapters = tool_adapters
        self.report_generators = report_generators
        self.error_analyst = error_analyst
        self.error_fixer = error_fixer
        self.tool_installer = tool_installer
        self.security_advisor = security_advisor
        self.network_agent = network_agent
        self.update_agent = update_agent
        self.config_manager = config_manager
        self.dependency_auditor = dependency_auditor
        self.knowledge_agent = knowledge_agent
        self.pentestgpt_agent = pentestgpt_agent
        self.logger = logger
        self.config = config
        self.audit_logger = audit_logger
        self.consent_service = consent_service
        self.execution_history = execution_history

    def _create_error_result(self, raw_command: str, message: str, tool_name: str = "unknown") -> ExecutionResult:
        return ExecutionResult(
            command=Command(tool_name=tool_name, raw_command=raw_command),
            success=False,
            output=message,
            error=Error(message=message)
        )

    async def handle_input(self, user_input: str) -> Any:
        self.logger.log(f"Received new input: '{user_input}'. Interpreting intent...", level=LogLevel.INFO)

        if not self.network_agent.check_internet_connection():
            error_message = "[NetworkAgent] No internet connection. AI features unavailable."
            self.logger.log(error_message, level=LogLevel.ERROR)
            return self._create_error_result(user_input, error_message)

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
            return await self.pentestgpt_agent.setup_and_run(override_model=override_model)
        else:
            error_message = params.get("message", f"Could not understand the command: {user_input}")
            self.logger.log(error_message, level=LogLevel.ERROR)
            return self._create_error_result(user_input, error_message)

    async def _handle_knowledge_query(self, params: dict) -> str:
        question = params.get("question")
        if not question: return "Could not answer question: No question was provided."
        self.logger.log(f"Handling knowledge query: '{question}'", level=LogLevel.INFO)
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
        self.logger.log("Starting system update process...", level=LogLevel.INFO)
        framework_update_available = self.update_agent.check_framework_update()
        tool_updates = self.update_agent.check_tool_updates()
        pip_updates_available = bool(tool_updates.get("pip"))
        pkg_updates_available = bool(tool_updates.get("pkg"))
        if not framework_update_available and not pip_updates_available and not pkg_updates_available:
            self.logger.log("System is already up to date.", level=LogLevel.INFO)
            return "System is already up to date."
        summary = "Updates are available for the following components:\n"
        if framework_update_available: summary += "- The main framework\n"
        if pkg_updates_available: summary += "- System packages (via pkg)\n"
        if pip_updates_available: summary += f"- Pip packages: {', '.join(tool_updates['pip'])}\n"
        summary += "\nDo you want to apply these updates?"
        update_command = Command(tool_name="system-update", args=[], raw_command="update", is_dangerous=True)
        if self.consent_service.get_consent(update_command, summary_prompt=summary):
            self.logger.log("User consented to updates. Applying now...", level=LogLevel.INFO)
            result_message = ""
            if framework_update_available:
                result_message += f"Framework update: {self.update_agent.apply_framework_update()}\n"
            if pkg_updates_available or pip_updates_available:
                result_message += f"Tool update: {self.update_agent.apply_tool_updates(pip_packages=tool_updates.get('pip', []))}\n"
            return result_message.strip() or "Update process finished."
        else:
            self.logger.log("User did not consent to updates. Aborting.", level=LogLevel.WARNING)
            return "Update process aborted by user."

    async def _handle_run_tool(self, user_input: str) -> ExecutionResult:
        try:
            command = await self.tool_command_parser.parse_command(user_input)
            consent_given = self.consent_service.get_consent(command)
            if not self.config.dry_run and not consent_given:
                result = self._create_error_result(user_input, "User did not provide consent.", command.tool_name)
                result.consent_given = False
                self._finalize_execution(result)
                return result
            result = await self._run_command_flow(command)
            result.consent_given = consent_given
            if not result.success and result.error: await self._enrich_failed_result(result)
            elif result.success: await self._enrich_successful_result(result)
        except (ValueError, RuntimeError, ConnectionError, PermissionError) as e:
            self.logger.log(f"A critical error occurred during tool execution: {e}", level=LogLevel.ERROR)
            result = self._create_error_result(user_input, str(e), "framework")
        self._finalize_execution(result)
        return result

    async def _enrich_failed_result(self, result: ExecutionResult):
        self.logger.log("Command failed. Consulting Error Analyst and Error Fixer Agents...", level=LogLevel.WARNING)
        analysis_task = self.error_analyst.analyze_error(result.command, result.error)
        fix_task = self.error_fixer.suggest_fix(result.command, result.error)
        analysis, fixed_command = await asyncio.gather(analysis_task, fix_task)
        result.error.ai_analysis = analysis
        if fixed_command: result.error.message += f"\n\n[bold yellow]AI Suggested Fix:[/bold yellow]\n{' '.join([fixed_command.tool_name] + fixed_command.args)}"

    async def _enrich_successful_result(self, result: ExecutionResult):
        self.logger.log("Command successful. Consulting Security Advisor Agent...", level=LogLevel.INFO)
        result.ai_advice = await self.security_advisor.provide_advice(result)

    def _finalize_execution(self, result: ExecutionResult):
        self.logger.log("Generating reports.")
        paths = result.paths
        if paths:
            for report_generator in self.report_generators: report_generator.generate(result, paths)
            paths.report_files = [os.path.join(paths.run_dir, f"{paths.base_filename}.txt"), os.path.join(paths.run_dir, f"{paths.base_filename}.json")]
            artifact_paths = paths.report_files[:]
            if paths.output_log_file: artifact_paths.append(str(paths.output_log_file))
            self.audit_logger.append({"session_id": self.config.session_id, "command": result.command.raw_command, "tool": result.command.tool_name, "exit_code": result.error.error_code if result.error else 0, "error_message": result.error.message if result.error else None, "artifact_paths": artifact_paths})
        self.execution_history.append(result)

    async def _run_command_flow(self, command: Command) -> ExecutionResult:
        self.logger.log(f"Finding adapter for tool '{command.tool_name}'.")
        adapter = self.tool_adapters.get(command.tool_name.lower())
        if not adapter: raise ValueError(f"Tool '{command.tool_name}' is not supported.")
        tool = adapter.find_tool(command.tool_name)
        if not tool: raise ValueError(f"Tool '{command.tool_name}' not found by adapter.")
        self.tool_installer.install_if_needed(tool)
        self.logger.log(f"Using adapter '{adapter.__class__.__name__}' for command '{command.tool_name}'.")
        paths = self.report_generators[0].prepare_report_paths(command.tool_name) if self.report_generators else RunPaths(run_dir=".", base_filename="dry_run")
        if self.config.dry_run: return ExecutionResult(command=command, success=True, output="Dry run: command not executed.", paths=paths)
        result = adapter.run(tool, command, paths)
        result.paths = paths
        result.output_log_file = str(paths.output_log_file) if paths else None
        return result
