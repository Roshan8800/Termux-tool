# Termux Cyber Framework

**Created by Roshan**

An advanced, AI-driven cybersecurity framework designed for simplicity, automation, and extensibility. Run complex penetration testing workflows with simple, natural language commands.

---

## Overview

This framework allows users to run a variety of cybersecurity tools and complex workflows using natural language. It leverages the Google Gemini API to interpret your intent and orchestrates a suite of specialized agents to perform tasks, from running simple commands to fully automating the setup and execution of sophisticated tools like PentestGPT with local LLMs.

The system is designed with a robust, agent-based architecture that is secure, user-friendly, and easily extensible.

## Key Features

- **Natural Language Command Interface:** The primary way to interact is through the global `cyber` command, which accepts plain English.
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

---

## Quick Installation

Getting started is designed to be as simple as possible. You only need to run two commands.

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/your-repo/termux-cyber-framework.git
    cd termux-cyber-framework
    ```

2.  **Run the Setup Script**
    This one-time setup script checks for dependencies, installs the framework, and makes the `cyber` command available globally.
    ```bash
    bash first_run_setup.sh
    ```

That's it! The script is idempotent (safe to re-run). After setup is complete, you can start using the `cyber` command immediately.

---

## How to Use

After installation, the `cyber` command is the main entry point to the framework.

### Interactive Shell (Recommended)

To launch the interactive shell for a full session, which is the recommended way to use the tool:
```bash
cyber framework shell
```
This will display a welcome banner on your first run and then drop you into the `cyber-ai>` prompt, where you can enter natural language commands directly.

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

### System Health Check

If you suspect something is not working correctly, you can run the built-in doctor command to diagnose your setup:
```bash
cyber framework doctor
```
This will check your configuration, API key connectivity, and tool installations, then provide a clean report.
