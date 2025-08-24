# Termux Cyber Framework

**Created by Roshan**

An advanced, AI-driven cybersecurity framework designed for simplicity, automation, and extensibility. Run complex penetration testing workflows with simple, natural language commands.

---

## Overview

This framework allows users to run a variety of cybersecurity tools and complex workflows using natural language. It leverages the Google Gemini API to interpret your intent and orchestrates a suite of specialized agents to perform tasks, from running simple commands to fully automating the setup and execution of sophisticated tools like PentestGPT with local LLMs.

The system is designed with a robust, agent-based architecture that is secure, user-friendly, and easily extensible.

## Key Features

- **Natural Language Command Interface:** The primary way to interact is through the `run` command or the interactive `shell`, which accept plain English commands.
- **Agent-Based Architecture:** A powerful multi-agent system, led by a central `OrchestratorAgent`, delegates tasks to specialized agents for tool installation, execution, error analysis, and more.
- **Automated PentestGPT & Ollama Integration:**
    - **Zero-Setup Analysis:** Run a command like `"start a pentest session"` and the framework will automatically handle the entire setup.
    - **System-Aware:** Checks for available storage before downloading large language models.
    - **Dynamic Model Selection:** Intelligently chooses the best local LLM (e.g., Llama3, Phi3) that fits your device's storage capacity.
    - **Fully Automated:** Installs Ollama, PentestGPT, and all dependencies automatically.
    - **Local & Private:** Runs the analysis on your device using a local Ollama server, ensuring privacy.
- **Automated Tool Installation:** The framework automatically installs any required tool on-demand using the appropriate method (`apt-get`, `pkg`, `pip`, `git`, or `shell` scripts).
- **Multi-Format Reporting:** Generates detailed reports for every operation in four formats: **TXT**, **JSON**, **Markdown**, and **PDF**.
- **User Consent Flow:** For potentially dangerous operations, the framework prompts for explicit user consent before proceeding.

---

## Installation

Getting the framework up and running is simple.

### Prerequisites

- **Python 3.11+**
- **Poetry**: For managing Python dependencies.
- **Git**

### Automated Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/your-repo/termux-cyber-framework.git
    cd termux-cyber-framework
    ```

2.  **Run the Setup Script**
    This script will automatically detect your OS (Termux, Kali, etc.), install necessary system packages (like `build-essential`), and then use `poetry` to install all required Python libraries.
    ```bash
    bash install.sh
    ```

That's it! The script will handle everything for you.

---

## How to Use

The framework is designed to be intuitive. The primary entry points are the `run` and `shell` commands, which are best invoked through the `poetry run` command to ensure you're using the correct environment.

### Interactive Shell (Recommended)

To launch the interactive shell for a full session:
```bash
poetry run tcf shell
```
This will drop you into the `cyber-ai>` prompt, where you can enter natural language commands directly.

**Meta-Commands:**
- `:help` - Shows a help message.
- `:exit` - Exits the shell.

### Direct Command Execution

To run a single command without entering the shell, use the `run` command:
```bash
poetry run tcf run "your natural language command here"
```

### Examples

**1. Run a simple tool:**
```bash
poetry run tcf run "scan example.com for open ports with nmap"
```

**2. Get information about a tool:**
```bash
poetry run tcf run "what is sqlmap?"
```

**3. Start an automated PentestGPT session:**
```bash
poetry run tcf run "run a pentest analysis"
```
The framework will handle checking storage, selecting a model, installing everything, and launching the interactive PentestGPT session for you.

### Dry-Run Mode

If you want to see what the AI will interpret your command as without actually executing it, use the `--dry-run` flag.

```bash
poetry run tcf run "scan example.com" --dry-run
```

### Understanding the Output

After each command, you will receive a summary report in your console. Detailed reports in **TXT, JSON, Markdown, and PDF** format will be saved in the `reports/` directory, organized by date and tool name.
