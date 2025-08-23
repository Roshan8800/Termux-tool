# Tech Context

## 1. Core Framework & Libraries

- **Python 3.11+**: The primary programming language.
- **Typer**: Used for creating the command-line interface (`run` and `shell` commands). It provides automatic help generation and argument parsing.
- **Rich**: A dependency of Typer, used extensively for creating professional and user-friendly console output, including colored text, tables, and panels.
- **Pydantic**: Used for data modeling and validation (e.g., `Command`, `ExecutionResult`, `Tool` models). This ensures data consistency throughout the application.

## 2. AI Integration

- **Google Gemini API**: The primary AI model used for all intelligent tasks.
- **`google-genai` Library**: The official Python SDK for interacting with the Gemini API.
- **API Key**: The API key is currently hardcoded in `main.py` and `ai_interpreter.py`. **TODO:** This must be moved to a secure environment variable or configuration file.

## 3. Dependencies & Package Management

- **`requirements.txt`**: The list of Python dependencies for the project.
- **`pip`**: The package installer used to install the Python dependencies.
- **System Package Managers**: The `ToolInstallerAgent` supports `apt-get` (for Debian-based systems like Kali/Parrot) and `pkg` (for Termux) to install tool-specific dependencies.

## 4. Setup and Configuration

- **`install.sh`**: An automated setup script handles the installation of all necessary system-level and Python dependencies.
- **`data/tool_catalog.json`**: A central JSON file that acts as a catalog for all supported tools, defining their installation method, run commands, and any specific adapters.

## 5. Testing

- **Pytest**: The framework used for running all unit and integration tests.
- **`pytest-asyncio`**: A pytest plugin used for testing `async` code.
- **Mocks**: A `tests/mocks.py` file contains various mock objects used to isolate components during unit testing.
