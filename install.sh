#!/bin/bash

# A script to automate the installation of the Termux Cyber Framework.
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
print_info "Installing system dependencies..."
if [ "$PKG_MANAGER" == "apt-get" ]; then
    $SUDO_CMD apt-get update
    $SUDO_CMD apt-get install build-essential python3-dev rustc -y
else # pkg
    pkg install build-essential python rust -y
fi

if [ $? -ne 0 ]; then
    print_error "Failed to install system dependencies. Please check your package manager."
    exit 1
fi
print_success "System dependencies installed successfully."

# 3. Install Python Dependencies
print_info "Installing Python dependencies from requirements.txt..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    print_error "Failed to install Python dependencies. Please check your pip and internet connection."
    exit 1
fi
print_success "Python dependencies installed successfully."

# 4. Make the script executable (self-permissioning)
chmod +x install.sh

echo ""
print_success "Setup complete! You can now run the framework."
print_info "Example: python -m src.termux_cyber_framework.main run \"scan example.com for open ports\""
echo "========================================="
