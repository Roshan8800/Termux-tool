#!/bin/bash

# A user-friendly, idempotent setup script for the Termux Cyber Framework.

# --- Color Definitions ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# --- Helper Functions ---
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# --- Prerequisite Checks ---
print_info "Checking for required system dependencies..."

# Check for Git
if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install Git before running this script."
    exit 1
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3 before running this script."
    exit 1
fi

print_info "All system dependencies found."
echo ""

# --- Idempotency Check ---
# Check if the poetry environment already exists.
# `poetry env info -p` returns the path to the virtualenv. If it succeeds, we assume setup is done.
if poetry env info -p &> /dev/null; then
    print_warn "A Poetry environment already exists for this project."
    print_info "It seems the framework is already installed."
    echo ""
    print_info "To run the framework, use the following command:"
    echo -e "${GREEN}poetry run tcf shell${NC}"
    exit 0
fi


# --- Core Installation ---
print_info "No existing installation found. Starting the setup process..."
echo ""

# Check if install.sh exists and is executable
if [ -f "install.sh" ]; then
    chmod +x install.sh
    # Run the core installation script
    ./install.sh

    # Check the exit code of install.sh
    if [ $? -ne 0 ]; then
        print_error "The core installation script (install.sh) failed. Please check the output above for errors."
        exit 1
    fi
else
    print_error "Core installation script 'install.sh' not found. Aborting."
    exit 1
fi

# --- Final Guidance ---
echo ""
print_info "Setup is complete!"
print_info "You can now run the framework's interactive shell with the following command:"
echo ""
echo -e "  ${GREEN}poetry run tcf shell${NC}"
echo ""
print_warn "On your first run, the AI models may take some time to download."
