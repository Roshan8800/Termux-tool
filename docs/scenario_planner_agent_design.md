# Design Document: Scenario Planner Agent

## 1. Purpose

The Scenario Planner Agent is a high-level strategic agent within the Termux Cyber Framework. Its primary purpose is to take a broad, goal-oriented command from a user (e.g., "find and exploit web vulnerabilities on example.com") and decompose it into a logical, multi-step attack chain or "scenario." This moves the framework from executing single commands to orchestrating entire cybersecurity campaigns.

## 2. Integration into the Framework

The agent will be integrated into the `OrchestratorAgent`'s main command handling loop.

-   A new intent, `run_scenario`, will be added to the `MasterAIInterpreter`.
-   When this intent is detected, the `OrchestratorAgent` will invoke the `ScenarioPlannerAgent` with the user's high-level goal.
-   The `ScenarioPlannerAgent` will return a structured plan (a list of `Command` objects).
-   The `OrchestratorAgent` will then execute this sequence of commands one by one, feeding the output of one step into the planning of the next if necessary (this is an advanced concept for a future version; for V1, the plan is static).

## 3. Logic Flow

The internal logic of the `ScenarioPlannerAgent` will be as follows:

### Input:
-   `goal` (str): The high-level, natural language goal from the user.

### Output:
-   `plan` (List[Command]): A list of structured `Command` objects representing the attack chain.

### Steps:
1.  **Get Available Tools:** The agent will first retrieve the list of all available tools and their descriptions from the `ToolCatalog`. This is crucial for the AI to generate a realistic plan based on the framework's actual capabilities.
2.  **Build AI Prompt:** The agent will construct a detailed prompt for the Gemini AI model. The prompt will include:
    -   The user's high-level `goal`.
    -   The list of available tools and their purposes.
    -   A clear instruction to act as an expert penetration tester and create a step-by-step plan to achieve the goal.
    -   A strict directive to output the plan in a specific JSON format, representing a list of commands with tool names and arguments.
    -   An example of the desired JSON output to guide the model.
3.  **Generate Plan:** The agent will send the prompt to the AI model and receive the JSON-formatted plan.
4.  **Validate and Parse Plan:** The agent will validate that the AI's response is valid JSON and conforms to the expected structure. It will then parse this JSON into a list of Pydantic `Command` objects. If validation fails, the agent will return an empty plan or an error.
5.  **Return Plan:** The agent will return the final list of `Command` objects to the `OrchestratorAgent`.

## 4. Example AI Prompt

```
You are an expert cybersecurity strategist. Your task is to create a step-by-step penetration testing plan based on a user's goal and a list of available tools.

**User Goal:**
"Find and exploit SQL injection vulnerabilities on the login page of example.com"

**Available Tools:**
- nmap: A network scanner to find open ports and services.
- sqlmap: An automatic SQL injection and database takeover tool.
- nikto: A web server scanner which performs comprehensive tests.
- ... (and so on)

**Your Task:**
Create a JSON array of commands to achieve the user's goal. Each object in the array must have a "tool" and "args" key.

**Example JSON Output:**
[
  {
    "tool": "nmap",
    "args": ["-sV", "-p", "80,443", "example.com"]
  },
  {
    "tool": "sqlmap",
    "args": ["-u", "https://example.com/login", "--forms", "--batch"]
  }
]

Now, create the plan for the user goal provided above.
```

## 5. Dependencies

-   **Gemini AI Model:** For the core planning logic.
-   **`ToolCatalog`:** To provide the AI with a list of available tools.
-   **`OrchestratorAgent`:** To receive the high-level goal and to return the generated plan to.
