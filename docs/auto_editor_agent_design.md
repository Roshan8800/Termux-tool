# Design Document: Auto-Editor Agent

## 1. Purpose

The Auto-Editor Agent is a specialized agent within the Termux Cyber Framework responsible for automatically patching broken scripts found in external tools. When the framework attempts to run a tool and encounters a script-based error (e.g., syntax error, deprecated function), this agent will be invoked to attempt a fix, making the framework more resilient and self-healing.

## 2. Integration into the Framework

The Auto-Editor Agent will be integrated into the main error-handling workflow, coordinated by the `OrchestratorAgent`.

The flow will be as follows:
1.  The `OrchestratorAgent` executes a command using a tool.
2.  The command fails with an error.
3.  The `OrchestratorAgent` passes the error to the `ErrorAnalystAgent` to understand the error.
4.  The `ErrorAnalystAgent`'s analysis suggests the error is due to a flaw in the tool's script itself (e.g., a Python syntax error, a bash script error). This could be determined by keywords in the error message like `SyntaxError`, `NameError`, `command not found` within a script's context, etc.
5.  If the analysis points to a script error, the `OrchestratorAgent` will invoke the `AutoEditorAgent`.
6.  The `AutoEditorAgent` will attempt to patch the file.
7.  If the patch is successful, the `OrchestratorAgent` will retry the original command.

## 3. Logic Flow

The internal logic of the `AutoEditorAgent` will proceed as follows:

### Inputs:
-   `script_path` (str): The absolute path to the broken script file.
-   `error_message` (str): The stderr or error output from the failed command.
-   `original_command` (Command): The original command that was attempted.

### Steps:
1.  **Read Script:** The agent will first read the entire content of the file at `script_path`.
2.  **Build AI Prompt:** The agent will construct a detailed prompt for the Gemini generative AI model. The prompt will include:
    -   The full content of the broken script.
    -   The detailed error message.
    -   The command that triggered the error.
    -   A clear instruction to act as an expert programmer and provide a corrected version of the script.
    -   A directive to provide *only* the full, corrected script content, without any explanations or conversational text.
3.  **Generate Patch:** The agent will send the prompt to the AI model and receive the suggested new script content.
4.  **Validate Patch (Simplified):** For the initial version, validation will be simple:
    -   Check if the returned text is not empty and is substantially different from the original.
    -   A more advanced validation could involve using a linter (`pylint`, `shellcheck`) to check the syntax of the new script content before applying it.
5.  **Apply Patch:** If the validation passes, the agent will use the `overwrite_file_with_block` tool to replace the content of the broken script with the AI-generated fix.
6.  **Return Status:** The agent will return a boolean status indicating whether a patch was successfully applied.

## 4. Dependencies

The `AutoEditorAgent` will have the following dependencies:
-   **Gemini AI Model:** For generating the code patches.
-   **File System Access:** To read the original script and write the patched version. This will likely be managed through a `FileManagerAgent` or similar abstraction for security and logging.
-   **`OrchestratorAgent`:** To be invoked and to return the result to.

---
