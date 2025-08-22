# Termux Cyber Framework

**Created by Roshan**

A professional, AI-powered cybersecurity framework designed for simplicity and extensibility. Run complex tools with simple, natural language commands.

![CLI Screenshot](https://i.imgur.com/your-screenshot.png) <!-- Placeholder for a real screenshot -->

## Overview

This framework allows users to run a variety of cybersecurity tools using natural language commands. It leverages the Google Gemini API to interpret your intent, select the appropriate tool, and execute it. It's designed to be extensible, secure, and user-friendly, with a focus on clear reporting and user consent for potentially dangerous operations.

## Key Features

- **AI-Powered Command Interpretation:** Simply tell the framework what you want to do in plain English (e.g., `"scan example.com for open ports"`).
- **Cross-Platform Support:** Works on various Debian-based systems, including **Termux**, **Kali Linux**, and **Parrot OS**.
- **Automated Tool Installation:** The framework automatically installs the necessary tools on-demand using the appropriate package manager (`apt-get` or `pkg`).
- **Enhanced Reporting:** Generates detailed reports for every operation in both `.txt` and `.json` formats, including metadata like execution time, AI interpretation, and user consent.
- **User Consent Flow:** For potentially dangerous operations (e.g., `sqlmap`), the framework will prompt for explicit user consent before proceeding.
- **Modular Architecture:** Easily extend the framework by adding new tools to the tool catalog.

---

## Installation

Getting the framework up and running is simple, thanks to the automated setup script.

### Prerequisites

- **Git**
- An active internet connection.
- A supported operating system (Termux, Kali Linux, Parrot OS).

### Automated Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/your-repo/termux-cyber-framework.git
    cd termux-cyber-framework
    ```

2.  **Run the Setup Script**
    This script will automatically detect your OS, install necessary system packages, and then install all the required Python libraries.
    ```bash
    bash install.sh
    ```

That's it! The script will handle everything for you. On systems like Kali or Parrot, it may ask for your `sudo` password to install system packages.

---

## How to Use

The framework is designed to be intuitive. You interact with it using the `run` command followed by your command in plain English.

### Basic Usage

To run a command, use the following structure:
```bash
python -m src.termux_cyber_framework.main run "your natural language command"
```

### Examples

Here are a few examples of how you can use the framework:

**1. Scan for open ports on a domain:**
```bash
python -m src.termux_cyber_framework.main run "scan example.com for open ports with nmap"
```

**2. Check a website for SQL injection vulnerabilities:**
```bash
python -m src.termux_cyber_framework.main run "check example.com for SQL injection"
```
*(This is a dangerous command and will trigger a consent prompt.)*

**3. Get WHOIS information for a domain:**
```bash
python -m src.termux_cyber_framework.main run "whois google.com"
```

### Dry-Run Mode

If you want to see what the AI will interpret your command as without actually executing it, use the `--dry-run` flag. This is great for testing or learning how the framework works.

```bash
python -m src.termux_cyber_framework.main run "scan example.com for open ports" --dry-run
```

### Understanding the Output

After each command, you will receive a summary report in your console. Detailed reports in both `.txt` and `.json` format will be saved in the `reports/` directory, organized by date and tool name.

---

## Architecture

The framework is built using a hexagonal architecture, with a core domain that is independent of the adapters. This keeps the core logic clean and makes the framework easy to maintain and extend.

- **Core**: Contains the domain models, use cases, and ports.
- **Adapters**: Implement the ports and provide the concrete implementations for the framework's features (e.g., AI Interpreter, Reporters, Tool Installers).
- **CLI**: The command-line interface, built with `Typer` and `rich`.

The `main.py` file in the `src/termux_cyber_framework/adapters/cli` directory acts as the **Composition Root**, where all the adapters are instantiated and wired together.
