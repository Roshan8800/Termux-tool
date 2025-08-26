# Design Document: Data Collector Agent

## 1. Purpose

The Data Collector Agent is a specialized agent responsible for processing the output of various cybersecurity tools and structuring it into a consistent, centralized format. Its goal is to transform raw text output from scans and analyses into a structured database of findings (e.g., open ports, vulnerabilities, credentials). This collected data can then be used for report generation, further analysis by other agents, or to inform subsequent steps in a planned scenario.

## 2. Integration into the Framework

The `DataCollectorAgent` will be integrated into the `OrchestratorAgent`'s execution finalization process.

-   The agent will be instantiated in `main.py` and passed to the `OrchestratorAgent`.
-   The `OrchestratorAgent`'s `_finalize_execution` method will be modified. After a tool command executes successfully, the `OrchestratorAgent` will pass the `ExecutionResult` object to the `DataCollectorAgent`.
-   The `DataCollectorAgent` will then process the result in the background.

## 3. Logic Flow

The internal logic of the `DataCollectorAgent` will be as follows:

### Input:
-   `result` (ExecutionResult): The complete result object from a successful tool execution, containing the command run, the tool name, and the raw output.

### Steps:
1.  **Determine Output Type:** The agent will first identify the tool that produced the output (from `result.command.tool_name`). This is important because parsing the output depends heavily on the tool (e.g., parsing `nmap` output is different from `sqlmap` output).
2.  **Build AI Prompt for Extraction:** The agent will construct a specialized prompt for the Gemini AI model, tailored to the specific tool. The prompt will include:
    -   The raw text output from the tool (`result.output`).
    -   A clear instruction to act as a data extraction expert.
    -   A directive to extract key findings and structure them into a specific JSON format. The format will depend on the tool. For example, for `nmap`, it would be a list of objects with `port`, `state`, `service`, and `version`.
    -   An example of the desired JSON output.
3.  **Extract and Structure Data:** The agent will send the prompt to the AI and receive the structured JSON data.
4.  **Validate Data:** The agent will perform a basic validation to ensure the response is valid JSON and contains the expected keys.
5.  **Store Data:** The agent will append the structured data to a central data store. For V1, this will be a simple JSON file, `data/findings.json`. The agent will handle reading the existing file, appending the new findings, and writing the file back to disk, ensuring thread-safe operations if necessary.

## 4. Example AI Prompt (for Nmap)

```
You are a data extraction specialist. Your task is to parse the raw output from a tool and extract the key findings into a structured JSON format.

**Tool:**
"nmap"

**Raw Output:**
"""
Starting Nmap 7.92 ( https://nmap.org ) at 2023-10-27 10:00 EDT
Nmap scan report for example.com (93.184.216.34)
Host is up (0.011s latency).
Not shown: 998 filtered tcp ports
PORT    STATE SERVICE  VERSION
80/tcp  open  http     nginx 1.18.0
443/tcp open  ssl/http nginx 1.18.0

Nmap done: 1 IP address (1 host up) scanned in 7.47 seconds
"""

**Your Task:**
Extract all open ports and their associated services and versions.
Output the result as a JSON array of objects. Each object must have a "port", "state", "service", and "version" key.

**JSON Output:**
[
  {
    "port": "80/tcp",
    "state": "open",
    "service": "http",
    "version": "nginx 1.18.0"
  },
  {
    "port": "443/tcp",
    "state": "open",
    "service": "ssl/http",
    "version": "nginx 1.18.0"
  }
]
```

## 5. Dependencies

-   **Gemini AI Model:** For the data extraction and structuring logic.
-   **`OrchestratorAgent`:** To receive the `ExecutionResult` after a command is run.
-   **`FileManagerAgent` (or direct file access):** To read from and write to the `data/findings.json` data store.
