#!/usr/bin/env python
# src/termux_cyber_framework/main.py

"""
Main entry point for the Termux Cyber Framework application.
"""

from termux_cyber_framework.adapters.cli.main import app

def main():
    """
    This function launches the command-line interface.
    The composition of dependencies is handled within the CLI adapter.
    """
    app()

if __name__ == "__main__":
    main()
