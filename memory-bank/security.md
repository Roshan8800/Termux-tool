# Security & Compliance

This document outlines the security protocols, data privacy practices, and compliance information for the Termux Cyber Framework.

## Consent Flow
The framework has a built-in consent mechanism, managed by the `SecurityComplianceAgent`. For any tool marked as "dangerous" (e.g., `nmap`, `sqlmap`), the agent will prompt the user for explicit yes/no confirmation before execution. All consent decisions are logged in `reports/consent_log.json`.

## Data Handling
- The tool processes user commands and tool outputs.
- Reports and logs are stored locally in the `reports/` and `logs/` directories.
- The AI API key is currently hardcoded but should be moved to a secure environment variable.

*This document will be updated as new security features are added.*
