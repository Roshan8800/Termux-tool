# Tech Context

## 1. Core Framework & Libraries

- **Python 3.11+**: The primary programming language.
- **Poetry**: The dependency management and packaging tool used for the project.
- **Typer**: Used for creating the command-line interface (`run` and `shell` commands).
- **Pydantic**: Used for data modeling and validation (e.g., `Command`, `ExecutionResult`, `Tool` models), ensuring data consistency.

## 2. User Interface & Reporting

- **Rich**: A key library for creating professional and user-friendly console output, including colored text, tables, panels, and spinners.
- **fpdf2**: The library used by the `PdfReporter` to generate reports in PDF format.

## 3. AI Integration

- **Google Gemini API**: The primary AI model used for all intelligent tasks (intent recognition, error analysis, etc.).
- **`google-generativeai` Library**: The official Python SDK for interacting with the Gemini API.
- **Ollama**: The service used for running local large language models. The framework can install and manage the Ollama service.
- **API Key Management**: API keys are managed via the `ConfigManagerAgent`, which securely stores and retrieves them from a `config/config.json` file.

## 4. Dependencies & Package Management

- **`pyproject.toml`**: The file that defines all project metadata and dependencies for Poetry.
- **System Package Managers**: The `ToolInstallerAgent` supports `apt-get` (for Debian-based systems like Kali/Parrot) and `pkg` (for Termux).
- **Shell Scripts**: The `ToolInstallerAgent` can also run shell scripts for installation (e.g., for Ollama).
- **`pip`**: Used by the `GitInstallerAdapter` to automatically install dependencies from `requirements.txt` files found in cloned tool repositories.


## 5. Setup and Configuration

- **`install.sh`**: An automated setup script handles the installation of all necessary system-level and Python dependencies.
- **`data/tool_catalog.json`**: A central JSON file that acts as a catalog for all supported tools, defining their installation method, run commands, and any specific adapters.
- **`config/llm_models.json`**: A configuration file that lists recommended local LLMs and their storage requirements for dynamic model selection.

## 6. Testing

- **Pytest**: The framework used for running all unit and integration tests.
- **`pytest-asyncio`**: A pytest plugin used for testing `async` code.
- **Mocks**: A `tests/mocks.py` file contains various mock objects used to isolate components during unit testing.
