#!/bin/bash

# start_framework.sh
# A wrapper script to run the Termux Cyber Framework with crash detection and auto-restart.

LOG_DIR="logs"
CRASH_LOG="$LOG_DIR/crash.log"
MAX_RESTARTS=5
RESTART_DELAY=5 # seconds
RESTART_COUNT=0

# Ensure the log directory exists
mkdir -p $LOG_DIR

echo "Starting Termux Cyber Framework with monitoring..."

while [ $RESTART_COUNT -lt $MAX_RESTARTS ]; do
    # Launch the main application.
    # We run the cli main directly to start the application.
    python3 -m src.termux_cyber_framework.adapters.cli.main shell

    EXIT_CODE=$?

    if [ $EXIT_CODE -eq 0 ]; then
        # Exit code 0 means a clean exit (e.g., user typed ':exit')
        echo "Framework exited cleanly. Shutting down."
        break
    else
        # Non-zero exit code indicates a crash
        RESTART_COUNT=$((RESTART_COUNT + 1))
        TIMESTAMP=$(date)

        echo "[$TIMESTAMP] Framework crashed with exit code $EXIT_CODE." | tee -a $CRASH_LOG

        if [ $RESTART_COUNT -lt $MAX_RESTARTS ]; then
            echo "Attempting to restart in $RESTART_DELAY seconds... (Attempt $RESTART_COUNT/$MAX_RESTARTS)"
            sleep $RESTART_DELAY
        else
            echo "Maximum restart limit reached. The application will not be restarted again." | tee -a $CRASH_LOG
            break
        fi
    fi
done

echo "Framework monitoring has ended."
