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

if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install Git before running this script."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3 before running this script."
    exit 1
fi

print_info "All system dependencies found."
echo ""

# --- Idempotency Check ---
if poetry env info -p &> /dev/null; then
    print_warn "A Poetry environment already exists for this project."
    print_info "It seems the framework is already installed."
    echo ""
    print_info "To run the framework, try the following command:"
    echo -e "${GREEN}cyber framework shell${NC}"
    print_info "If that doesn't work, you can always use:"
    echo -e "${GREEN}poetry run tcf shell${NC}"
    exit 0
fi


# --- Core Installation ---
print_info "No existing installation found. Starting the setup process..."
echo ""

if [ -f "install.sh" ]; then
    chmod +x install.sh
    ./install.sh

    if [ $? -ne 0 ]; then
        print_error "The core installation script (install.sh) failed. Please check the output above for errors."
        exit 1
    fi
else
    print_error "Core installation script 'install.sh' not found. Aborting."
    exit 1
fi

# --- Alias Creation ---
print_info "Creating the 'cyber' command alias..."

# Determine the target directory for binaries
TARGET_DIR=""
if [[ "$OSTYPE" == "linux-android" ]]; then
    # Termux environment
    TARGET_DIR="/data/data/com.termux/files/usr/bin"
else
    # Standard Linux environment
    TARGET_DIR="/usr/local/bin"
fi

# Check if the target directory is in the PATH
if [[ ":$PATH:" == *":$TARGET_DIR:"* ]]; then
    # Create the symbolic link
    ln -sf "$(pwd)/cyber" "$TARGET_DIR/cyber"
    if [ $? -eq 0 ]; then
        print_info "Successfully created the 'cyber' command."
        print_info "You can now run the framework using 'cyber framework shell'."
    else
        print_error "Failed to create the 'cyber' command alias in $TARGET_DIR."
        print_warn "You may need to run this script with sudo, or create the alias manually."
        print_info "You can still run the framework using 'poetry run tcf shell'."
    fi
else
    print_warn "The target directory '$TARGET_DIR' is not in your \$PATH."
    print_warn "The 'cyber' command was not created automatically."
    print_info "To use the 'cyber' command, please add the following line to your shell profile (e.g., ~/.bashrc or ~/.zshrc):"
    echo -e "${GREEN}export PATH=\"$TARGET_DIR:\$PATH\"${NC}"
    print_info "For now, you can run the framework using 'poetry run tcf shell'."
fi


# --- Final Guidance ---
echo ""
print_info "Setup is complete!"
print_info "You can now run the framework's interactive shell with the following command:"
echo ""
echo -e "  ${GREEN}cyber framework shell${NC}"
echo ""
print_warn "On your first run, the AI models may take some time to download."
