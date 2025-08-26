#!/bin/bash

# A script to automate the installation of the Termux Cyber Framework.
# This script uses Poetry for robust dependency management.
# Created by Roshan.

echo "========================================="
echo "  Starting Termux Cyber Framework Setup  "
echo "========================================="

# Function to print colored messages
print_info() {
    echo -e "\e[34m[*] $1\e[0m"
}

print_success() {
    echo -e "\e[32m[+] $1\e[0m"
}

print_error() {
    echo -e "\e[31m[-] $1\e[0m"
}

# 1. Detect Package Manager
if command -v apt-get &> /dev/null; then
    PKG_MANAGER="apt-get"
    SUDO_CMD=""
    # Check if sudo is required
    if [ "$(id -u)" -ne 0 ]; then
        if ! command -v sudo &> /dev/null; then
            print_error "sudo is not installed. Please install it to proceed."
            exit 1
        fi
        SUDO_CMD="sudo"
    fi
    print_info "Debian-based system detected. Using apt-get."
elif command -v pkg &> /dev/null; then
    PKG_MANAGER="pkg"
    SUDO_CMD=""
    print_info "Termux detected. Using pkg."
else
    print_error "No supported package manager (apt-get, pkg) found. Please install dependencies manually."
    exit 1
fi

# 2. Install System Dependencies
print_info "Installing system dependencies (python, pip, rust, build-essential)..."
if [ "$PKG_MANAGER" == "apt-get" ]; then
    $SUDO_CMD apt-get update
    $SUDO_CMD apt-get install -y python3 python3-pip python3-dev build-essential rustc
else # pkg
    pkg install -y python python-pip build-essential rust
fi

if [ $? -ne 0 ]; then
    print_error "Failed to install system dependencies. Please check your package manager."
    exit 1
fi
print_success "System dependencies installed successfully."

# 3. Install Poetry
print_info "Checking for and installing Poetry..."
if ! command -v poetry &> /dev/null; then
    print_info "Poetry not found. Installing via pip..."
    pip install poetry
    if [ $? -ne 0 ]; then
        print_error "Failed to install Poetry. Please check your pip installation."
        exit 1
    fi
    # Add poetry to path for the current session
    export PATH="$HOME/.local/bin:$PATH"
    print_success "Poetry installed successfully."
else
    print_success "Poetry is already installed."
fi

# 4. Install Project Dependencies with Poetry
print_info "Installing project dependencies using Poetry..."
# We run this from the script's directory to ensure it finds pyproject.toml
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
(cd "$SCRIPT_DIR" && poetry install)

if [ $? -ne 0 ]; then
    print_error "Failed to install project dependencies with Poetry. Please check the output above."
    exit 1
fi
print_success "Project dependencies installed successfully."


# 5. Make the script executable (self-permissioning)
chmod +x install.sh

echo ""
print_success "Core installation complete!"
print_info "The 'first_run_setup.sh' script will now create the 'cyber' command for you."
echo "========================================="
