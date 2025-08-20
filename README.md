# Termux Cyber Framework

An AI-powered cybersecurity framework for Termux, designed with a clean, maintainable, and scalable architecture. This project combines principles from **Clean Architecture** and **Hexagonal Architecture (Ports and Adapters)** to create a system that is independent of frameworks, UI, and databases.

## Core Principles

- **Separation of Concerns**: The project is divided into two main areas:
    - **Core**: Contains the high-level business logic (Entities and Use Cases). It is completely independent and has no knowledge of external systems.
    - **Adapters**: Contain the implementations for external systems (e.g., CLI, database, network scanners). They depend on the Core but not on each other.
- **Dependency Inversion**: The Core defines interfaces (**Ports**), and the Adapters provide the concrete implementations. This inverts the control flow, making the Core the center of the application.

## Project Structure

```
.
├── src/
│   └── termux_cyber_framework/
│       ├── core/                 # Application Core (Business Logic)
│       │   ├── domain/           # - Domain Models (Entities)
│       │   └── use_cases/        # - Use Cases & Ports (Interfaces)
│       ├── adapters/             # Infrastructure (External tools)
│       │   ├── cli/              # - CLI Adapter (Primary)
│       │   ├── db/               # - Database Adapter (Secondary)
│       │   └── scanner/          # - Network Scanner Adapter (Secondary)
│       └── main.py               # Application Entry Point
├── pyproject.toml                # Project metadata and dependencies
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.9+
- [Poetry](https://python-poetry.org/) for dependency management.

### Installation

1.  Clone the repository:
    ```bash
    git clone <repository-url>
    cd termux-cyber-framework
    ```

2.  Install dependencies using Poetry:
    ```bash
    poetry install
    ```

### Usage

The framework provides a command-line interface. You can run commands via `poetry run`.

**Example: Scan a network**

```bash
poetry run tcf scan --ip-range 192.168.1.0/24
```

This will execute the network scanning use case using the currently configured adapters (in this initial version, it uses a mock scanner).

## Development

To run tests:
```bash
poetry run pytest
```
