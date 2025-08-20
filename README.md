# Termux Cyber Framework

A natural language-powered cybersecurity framework for Termux.

## Overview

This framework allows users to run cybersecurity tools using natural language commands. It is designed to be extensible, allowing new tools and features to be added easily.

## Architecture

The framework is built using a hexagonal architecture, with a core domain that is independent of the adapters. The main components are:

- **Core**: Contains the domain models, use cases, and ports.
- **Adapters**: Implement the ports and provide the concrete implementations for the framework's features.
- **CLI**: The command-line interface, built with Typer.

The `main.py` file in the `adapters/cli` directory acts as the composition root, where all the adapters are instantiated and wired together.

## How to Run in Dry-Run Mode

The framework supports a `--dry-run` flag that allows you to see what commands would be executed without actually running them. This is useful for testing and for CI environments.

To run in dry-run mode, use the `--dry-run` flag with the `run` command:

```
python -m termux_cyber_framework.adapters.cli.main run "scan example.com for open ports" --dry-run
```

## How to Add Tools

To add a new tool, you need to add an entry to the `config/tools.json` file. Each entry should have the following format:

```json
{
    "name": "tool_name",
    "description": "A description of the tool.",
    "install_info": {
        "method": "installation_method",
        "source": "installation_source"
    },
    "run_command": "base_run_command",
    "adapter_class": "full.path.to.adapter.class"
}
```

- `name`: The name of the tool.
- `description`: A brief description of the tool.
- `install_info`: An object with the installation method (`git`, `pip`, `pkg`) and source (URL, package name).
- `run_command`: The base command to execute the tool.
- `adapter_class`: The full import path to the tool's specific adapter class. If this is `null`, the `GenericRunner` will be used.

## How to Add Doctor Rules

To add a new doctor rule, you need to add an entry to the `config/doctor_rules.json` file. Each entry should have the following format:

```json
{
    "id": "rule_id",
    "pattern": "regex_pattern",
    "explain": "Explanation of the issue.",
    "commands": ["command_to_fix_the_issue"],
    "require_confirm": true
}
```

- `id`: a unique identifier for the rule.
- `pattern`: a regex pattern to match against the tool's output.
- `explain`: an explanation of the issue and the proposed fix.
- `commands`: a list of commands to run to fix the issue.
- `require_confirm`: a boolean indicating whether the user's confirmation is required before applying the fix.
