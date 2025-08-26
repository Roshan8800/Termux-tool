# Termux Cyber Framework

An advanced, AI-driven cybersecurity framework designed for simplicity, automation, and extensibility. Run complex penetration testing workflows with simple, natural language commands.

---

## Overview

This framework allows users to run a variety of cybersecurity tools and complex workflows using natural language. It leverages the Google Gemini API to interpret your intent and orchestrates a suite of specialized agents to perform tasks, from running simple commands to fully automating the setup and execution of sophisticated tools like PentestGPT with local LLMs.

The system is designed to be secure, user-friendly, and easily extensible, with a robust agent-based architecture at its core.

## Key Features

- **Natural Language Command Interface:** Interact with the framework using plain English through the global `cyber` command.
- **Agent-Based Architecture:** A powerful multi-agent system, led by a central `OrchestratorAgent`, delegates tasks to specialized agents for tool installation, execution, error analysis, and more.
- **Automated PentestGPT & Ollama Integration:**
    - **Zero-Setup Analysis:** Run `cyber framework run "start a pentest session"` and the framework will automatically handle the entire setup.
    - **System-Aware:** Checks for available storage before downloading large language models.
    - **Dynamic Model Selection:** Intelligently chooses the best local LLM that fits your device's storage capacity.
    - **Fully Automated:** Installs Ollama, PentestGPT, and all dependencies on first use.
    - **Local & Private:** Runs analysis on your device using a local Ollama server, ensuring privacy.
- **Automated Tool Installation:** Automatically installs any required tool on-demand using the appropriate method (`apt-get`, `pkg`, `pip`, `git`, or `shell` scripts).
- **Multi-Format Reporting:** Generates detailed reports for every operation in four formats: **TXT**, **JSON**, **Markdown**, and **PDF**.
- **System Health Checks:** A built-in `doctor` command helps diagnose issues with your installation and configuration.


## How It Works: The Agent-Based Architecture

The framework's intelligence comes from its modular, agent-based design. Here’s a simplified look at how it operates:

1.  **OrchestratorAgent:** When you issue a command (e.g., `"scan example.com for open ports with nmap"`), the `OrchestratorAgent` is the first to receive it.
2.  **Task Delegation:** The Orchestrator analyzes your request and delegates the task to the appropriate specialized agent. For the example above, it would activate the `ToolRunningAgent`.
3.  **Specialized Agents:** The framework includes a variety of agents, each with a specific role:
    - **ToolInstallerAgent:** Automatically installs missing tools.
    - **ErrorAnalystAgent:** Diagnoses and attempts to fix errors.
    - **KnowledgeAgent:** Provides information about tools.
    - **PentestGPTAgent:** Manages complex, multi-step penetration testing sessions.
    - ...and many more.
4.  **Execution & Reporting:** The assigned agent completes the task and generates a detailed report.

This modular architecture makes the framework highly extensible. New tools and capabilities can be added by creating new agents.

---

## Quick Installation

Getting started is simple. You only need to run two commands.

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/termux-create/termux-cyber-framework.git
    cd termux-cyber-framework
    ```

2.  **Run the Setup Script**
    This one-time setup script installs all necessary dependencies (including Poetry) and makes the `cyber` command available globally.
    ```bash
    bash first_run_setup.sh
    ```

That's it! The script is idempotent (safe to re-run). After setup, you can start using the `cyber` command immediately.

---

## How to Use

The `cyber` command is the main entry point to the framework.

### Interactive Shell (Recommended)

For an immersive session, launch the interactive shell:
```bash
cyber framework shell
```
This will display a welcome banner and drop you into the `cyber-ai>` prompt, where you can enter natural language commands directly.

### Direct Command Execution

To run a single command without entering the shell, use the `run` command:
```bash
cyber framework run "your natural language command here"
```

### Examples

**1. Run a simple tool:**
```bash
cyber framework run "scan example.com for open ports with nmap"
```

**2. Get information about a tool:**
```bash
cyber framework run "what is sqlmap?"
```

**3. Start an automated PentestGPT session:**
```bash
cyber framework run "start a pentest analysis"
```

---

## System Health Check

If you suspect something is not working correctly, run the built-in doctor command to diagnose your setup:
```bash
cyber framework doctor
```
This will check your configuration, API key connectivity, and tool installations, then provide a clean report.

---

## Development

Interested in contributing? Here’s how to get your development environment set up.

1.  **Fork and Clone:** Fork the repository and clone it to your local machine.
2.  **Install Dependencies:** Run the setup script to install all base dependencies.
    ```bash
    bash first_run_setup.sh
    ```
3.  **Activate Virtual Environment:** The script uses Poetry to manage dependencies. To activate the virtual environment, run:
    ```bash
    poetry shell
    ```
4.  **Run Tests:** We use `pytest` for testing. To run the full test suite:
    ```bash
    pytest
    ```
