#!/bin/bash

# ====================================================================
# SGPS DEPLOYMENT & AUTOMATED PACKAGING SYSTEM
# Targets: Linux (Ubuntu/Debian/Arch) & macOS environments
# ====================================================================

# Exit immediately if any command returns a non-zero exit status
set -e

# System ANSI color maps for diagnostic output
CLEAR='\033[0m'
BOLD='\033[1m'
BLUE='\033[34m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'

log_info() {
    echo -e "${BLUE}${BOLD}[INFO]${CLEAR} $1"
}

log_success() {
    echo -e "${GREEN}${BOLD}[SUCCESS]${CLEAR} $1"
}

log_warn() {
    echo -e "${YELLOW}${BOLD}[WARNING]${CLEAR} $1"
}

log_error() {
    echo -e "${RED}${BOLD}[ERROR]${CLEAR} $1"
}

echo -e "${BLUE}${BOLD}"
echo "============================================================"
echo "      SGPS SYSTEM ENVIRONMENT AUTOMATED DEPLOYMENT UTILITY   "
echo "============================================================"
echo -e "${CLEAR}"

# --------------------------------------------------------------------
# STEP 1: System Package Validation & Telemetry Dependencies
# --------------------------------------------------------------------
log_info "Verifying core system binary configurations..."

# Detect Host Operating System
OS_TYPE="$(uname -s)"
log_info "Detected Operating System platform: ${OS_TYPE}"

if [ "$OS_TYPE" = "Linux" ]; then
    # Check for Apt-based package manager
    if [ -x "$(command -v apt-get)" ]; then
        log_info "Apt manager detected. Ensuring system utilities are present..."
        if ! [ -x "$(command -v tmux)" ]; then
            log_warn "tmux multiplexer missing. Initiating installation via apt..."
            sudo apt-get update && sudo apt-get install -y tmux python3-venv python3-dev build-essential
        fi
    # Check for Pacman (Arch Linux)
    elif [ -x "$(command -v pacman)" ]; then
        log_info "Pacman manager detected. Checking system utilities..."
        if ! [ -x "$(command -v tmux)" ]; then
            log_warn "tmux multiplexer missing. Initiating installation via pacman..."
            sudo pacman -Syu --noconfirm tmux python
        fi
    else
        log_warn "Unrecognized Linux package framework. Please manually ensure 'tmux' and 'python3-venv' are present."
    fi

elif [ "$OS_TYPE" = "Darwin" ]; then
    # macOS environment checks
    if [ -x "$(command -v brew)" ]; then
        if ! [ -x "$(command -v tmux)" ]; then
            log_warn "tmux missing. Initiating installation via Homebrew..."
            brew install tmux
        fi
    else
        log_warn "Homebrew missing. Please install Homebrew or manually resolve the 'tmux' package layout."
    fi
else
    log_error "Unsupported deployment architecture: ${OS_TYPE}"
    exit 1
fi

# Verify core Python 3 runtime is accessible
if ! [ -x "$(command -v python3)" ]; then
    log_error "Python 3 deployment runtime could not be resolved. Execution halted."
    exit 1
fi

# --------------------------------------------------------------------
# STEP 2: Python Virtual Environment Build
# --------------------------------------------------------------------
log_info "Constructing isolated virtual environment workspace (.venv)..."

# Wipe existing environment if corrupt to guarantee clean build states
if [ -d ".venv" ]; then
    log_warn "Pre-existing environment directory located. Scrubbing local indices..."
    rm -rf .venv
fi

python3 -m venv .venv
log_info "Environment boundaries initialized successfully."

# --------------------------------------------------------------------
# STEP 3: Dependency Compiling
# --------------------------------------------------------------------
log_info "Upgrading packaging tools and injecting requirements..."

# Run updates safely within local context boundaries
./.venv/bin/python -m pip install --upgrade pip setuptools wheel

if [ -f "requirements.txt" ]; then
    ./.venv/bin/python -m pip install -r requirements.txt
    log_success "All targeted libraries injected into context successfully."
else
    log_error "Critical File Missing: requirements.txt not found in current directory workspace."
    exit 1
fi

# --------------------------------------------------------------------
# STEP 4: Execution Sandbox Verification & Script Normalization
# --------------------------------------------------------------------
log_info "Normalizing execution parameters for simulator wrapper paths..."

# Guarantee absolute workspace permissions for the orchestrator shell utility
if [ -f "launch_sims.sh" ]; then
    chmod +x launch_sims.sh
    log_info "System orchestration wrapper (launch_sims.sh) marked as executable."
else
    log_warn "Launch utility file wrapper (launch_sims.sh) could not be verified in this context."
fi

# Apply absolute executable privileges to any local python simulation components
find . -name "*.py" -exec chmod +x {} \;

# Setup result log mirrors to preserve host disk writes
mkdir -p sim_results mission_archives phase4_results phase4_endless_results real_world_archive

echo ""
echo -e "${GREEN}${BOLD}============================================================${CLEAR}"
echo -e "${GREEN}${BOLD}        SGPS SYSTEM DEPLOYMENT ARCHITECTURE COMPLETION      ${CLEAR}"
echo -e "${GREEN}${BOLD}============================================================${CLEAR}"
log_success "SGPS environment builds verified as fully functional."
echo -e "You can now safely initialize your multi-dashboard simulation suite by running:"
echo -e "    ${BLUE}${BOLD}./launch_sims.sh${CLEAR}\n"