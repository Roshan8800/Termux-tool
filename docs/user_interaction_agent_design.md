# Design Document: User Interaction Agent

## 1. Purpose

The User Interaction Agent will serve as the primary communication channel between the Termux Cyber Framework and the end-user. Its responsibility is to take structured data, such as execution results, errors, and scenario plans, and translate them into clear, concise, and helpful natural language. This will abstract away the raw technical output and provide a more polished, conversational user experience, reinforcing the framework's identity as an AI assistant.

## 2. Integration into the Framework

This agent will fundamentally change how results are presented to the user.

-   The `UserInteractionAgent` will be instantiated in `main.py` and passed to the `OrchestratorAgent`.
-   The `OrchestratorAgent` and the CLI view functions (in `adapters/cli/view.py`) will no longer be responsible for printing detailed results. Their role will be to pass the final, structured result objects to the `UserInteractionAgent`.
-   For example, in `_handle_run_tool`, after a result is finalized, instead of returning it to the CLI to be printed, it will be passed to `user_interaction_agent.present_result(result)`.
-   The `UserInteractionAgent` will then be responsible for all console output related to results.

## 3. Core Logic and Responsibilities

The agent will have a main entry point, `present_result(result_object)`, which will handle different types of results.

### Input:
-   `result_object` (Union[ExecutionResult, List[ExecutionResult], Error]): The object to be presented to the user.

### Logic Flow:
1.  **Result Routing:** The `present_result` method will check the type of the `result_object`.
    -   If it's a single successful `ExecutionResult`, it will call a `_summarize_success` method.
    -   If it's a single failed `ExecutionResult`, it will call an `_explain_error` method.
    -   If it's a list of `ExecutionResult` objects (from a scenario), it will call a `_summarize_scenario` method.
2.  **AI Prompt Generation:** Each of the specialized methods (`_summarize_success`, `_explain_error`, etc.) will build a specific prompt for the Gemini AI model. The prompt will instruct the AI to act as a helpful cybersecurity assistant and explain the provided data in natural language.
3.  **AI Summary Generation:** The agent will call the AI model to get the natural language explanation.
4.  **Display to User:** The agent will use the `rich` library to print the AI-generated summary to the console, likely within a formatted `Panel` for a clean presentation.

## 4. Example AI Prompts

### For a Successful Nmap Scan:
```
You are a helpful cybersecurity assistant. A user has just run a tool. Your task is to explain the results in a clear and simple way.

**Tool:**
"nmap"

**Command Run:**
"nmap -sV example.com"

**Raw Output:**
"""
PORT    STATE SERVICE  VERSION
80/tcp  open  http     nginx 1.18.0
443/tcp open  ssl/http nginx 1.18.0
"""

**Your Task:**
Summarize the key findings from this output. Explain what the open ports mean and suggest a potential next step.
```

### For a Failed Command:
```
You are a helpful cybersecurity assistant. A user's command has failed. Your task is to explain the error in a simple, non-technical way and offer advice.

**Command:**
"nmap -sU example.com"

**Error Message:**
"Permission denied. You need to be root to run this command."

**AI Analysis (from ErrorAnalystAgent):**
"The error indicates that the command requires root (administrator) privileges to run, which the user does not have."

**Your Task:**
Explain to the user why the command failed and what they should do next, based on the error and analysis.
```

## 5. Dependencies

-   **Gemini AI Model:** For generating the natural language explanations.
-   **`OrchestratorAgent`:** To receive the final result objects.
-   **`rich.console.Console`:** To print the formatted output to the user.
