# Termux Cyber Framework

**Your Personal Cybersecurity Assistant.**

---

## What is this?

The Termux Cyber Framework is a powerful tool that lets you run complex cybersecurity tasks using simple, everyday language. You don't need to be a security expert or memorize complicated commands. Just type what you want to do, and the framework's AI will handle the rest.

It's designed for simplicity, making advanced security tools accessible to everyone.

---

## How it Works

When you type a command in plain English, like "scan example.com for open ports," the framework's AI gets to work. It understands your request, selects the right tool for the job (like nmap), runs it, and gives you a clear report of the results. It can even install any missing tools automatically.

The entire process is automated, so you can focus on your tasks, not the technical details.

---

## Getting Started

Installation is designed to be as simple as possible.

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/termux-create/termux-cyber-framework.git
    cd termux-cyber-framework
    ```

2.  **Run the Setup Script**
    This one-time setup script will install everything you need.
    ```bash
    bash first_run_setup.sh
    ```

That's it! You're ready to go.

---

## How to Use

Using the framework is as simple as talking to an assistant.

**To start an interactive session:**
```bash
cyber
```
This will open a prompt (`cyber-ai>`). From there, just type what you want to do in plain English.

**To run a command directly:**
```bash
cyber your natural language command here
```

### Examples

Here are a few things you could ask the framework to do:

-   `cyber scan example.com for vulnerabilities`
-   `cyber what is sqlmap?`
-   `cyber find all subdomains of example.com`
-   `cyber start a pentest session`

---

## Development

Interested in contributing? Here’s how to get your development environment set up.

1.  **Fork and Clone:** Fork the repository and clone it to your local machine.
2.  **Install Dependencies:** Run the setup script to install all base dependencies.
    ```bash
    bash first_run_setup.sh
    ```
3.  **Activate Virtual Environment:** The script uses Poetry to manage dependencies. To activate the virtual environment, run:
    ```bash
    poetry shell
    ```
4.  **Run Tests:** We use `pytest` for testing. To run the full test suite:
    ```bash
    pytest
    ```
