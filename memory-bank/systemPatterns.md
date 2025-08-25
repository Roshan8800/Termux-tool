# System Patterns

## 1. High-Level Architecture

The framework is designed using a **Multi-Agent System architecture**, a modular, service-oriented design. The core principle is the separation of concerns, where different "agents" are responsible for specific tasks, all coordinated by a central orchestrator.

```mermaid
graph TD
    A[User Input] --> B[CLI / Shell];
    B --> C[OrchestratorAgent];

    subgraph "Core Brain"
        C
    end

    subgraph "Specialized Agents"
        D[AI-Powered Agents]
        E[Tool & System Management Agents]
        F[Reporting & I/O Agents]
    end

    C --> D
    C --> E
    C --> F

    subgraph "AI-Powered Agents"
        direction LR
        D_1[MasterAIInterpreter]
        D_2[ErrorAnalystAgent]
        D_3[SecurityAdvisorAgent]
        D_4[KnowledgeAgent]
    end

    subgraph "Tool & System Management Agents"
        direction LR
        E_1[ToolInstallerAgent]
        E_2[OllamaAdapter]
        E_3[PentestGptAgent]
        E_4[SystemResourceAgent]
        E_5[UpdateAgent]
        E_6[DoctorAgent]
    end

    subgraph "Reporting & I/O Agents"
        direction LR
        F_1[LoggerAgent]
        F_2[Report Generators\n(TXT, JSON, MD, PDF)]
        F_3[CommandRunner]
    end

    D --> E & F & C
    E --> F & C

    style "Core Brain" fill:#f9f,stroke:#333,stroke-width:2px
    style "Specialized Agents" fill:#ccf,stroke:#333,stroke-width:2px
```

## 2. Key Agents and Their Roles

- **`OrchestratorAgent`**: The central brain of the system. It uses the `MasterAIInterpreter` to understand the user's intent and delegates tasks to the appropriate specialized agent.

- **`MasterAIInterpreter`**: The first point of contact for AI interpretation. It analyzes the user's raw input to determine their high-level intent (e.g., `run_tool`, `update_system`, `run_pentest_analysis`).

- **`ToolInstallerAgent`**: Manages the installation of all tools. It uses the **Strategy Pattern** with different `InstallerStrategyPort` implementations (`Pkg`, `Git`, `Pip`, `Shell`) to handle various installation methods defined in the tool catalog.

- **`OllamaAdapter` & `PentestGptAgent`**: A pair of agents that work together to provide a powerful internal capability.
    - **`OllamaAdapter`** acts as a service manager for the local Ollama engine.
    - **`PentestGptAgent`** orchestrates the entire workflow of checking system resources, dynamically selecting a model, ensuring all dependencies are installed, and running a PentestGPT session. It's a prime example of an agent that consumes the services of other agents (`SystemResourceAgent`, `ToolInstallerAgent`, `OllamaAdapter`).

- **`SystemResourceAgent`**: An agent responsible for checking the state of the system, such as available storage space. Designed to be extensible for future checks like CPU and memory.

- **`DoctorAgent`**: A user-facing diagnostic agent. It runs a series of health checks (tool installation, config, API connectivity) and presents a clear report to the user to help them diagnose any issues.

- **`Report Generators`**: A set of classes that implement the `ReportGeneratorPort`. The system now supports generating reports in TXT, JSON, Markdown, and PDF formats after every command execution.

## 3. Key Design Patterns & Technical Rationale

- **Agent-Based Architecture:** Each agent has a single, well-defined responsibility (e.g., logging, installation, error analysis). This promotes high cohesion and low coupling, making the system easier to maintain, test, and extend.

- **Dependency Injection / Composition Root:** All components and agents are instantiated and "wired together" in a single place: the `build_agent_system` function in `src/termux_cyber_framework/adapters/cli/main.py`. This makes dependencies explicit and centralizes the application's construction logic.

- **Ports and Adapters (Hexagonal Architecture):** The core logic (the orchestrator and other agents) is decoupled from the concrete implementation of the services it uses (like specific reporters or installers).

- **Strategy Pattern:** The `ToolInstallerAgent` uses this pattern to select the correct installation method at runtime based on the tool's configuration in the catalog.
