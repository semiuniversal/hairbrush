#!/bin/bash

# Colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Environment variables
VENV_NAME="venv_hairbrush"
VENV_PATH="./${VENV_NAME}"
echo "VENV_PATH: ${VENV_PATH}"

# Function to display usage information
show_help() {
    echo -e "${BLUE}H.Airbrush Environment Management Script${NC}"
    echo -e "Usage: ./run.sh [command]"
    echo
    echo "Commands:"
    echo -e "  ${GREEN}start${NC}       - Activate the virtual environment"
    echo -e "  ${GREEN}stop${NC}        - Deactivate the virtual environment"
    echo -e "  ${GREEN}build${NC}       - Create and set up the virtual environment"
    echo -e "  ${GREEN}rebuild${NC}     - Recreate the virtual environment from scratch"
    echo -e "  ${GREEN}clean${NC}       - Remove the virtual environment"
    echo -e "  ${GREEN}run${NC}         - Start the Flask web server"
    echo -e "  ${GREEN}test${NC}        - Run tests"
    echo -e "  ${GREEN}help${NC}        - Show this help message"
}

# Function to create and set up the virtual environment
build_env() {
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    
    # Check if uv is installed
    if ! command -v uv &> /dev/null; then
        echo -e "${RED}Error: uv is not installed. Please install it first.${NC}"
        echo -e "You can install it with: pip install uv"
        exit 1
    fi
    
    # Create virtual environment using uv
    uv venv ${VENV_PATH}
    
    # Activate the virtual environment
    source ${VENV_PATH}/bin/activate
    
    # Install dependencies from pyproject.toml
    echo -e "${YELLOW}Installing dependencies...${NC}"
    uv pip install -e .
    
    echo -e "${GREEN}Virtual environment created and dependencies installed.${NC}"
    echo -e "You can activate it with: ${BLUE}source ${VENV_PATH}/bin/activate${NC}"
}

# Function to activate the virtual environment
start_env() {
    if [ ! -d "${VENV_PATH}" ]; then
        echo -e "${RED}Virtual environment not found. Creating it now...${NC}"
        build_env
    else
        echo -e "${GREEN}Activating virtual environment...${NC}"
        source ${VENV_PATH}/bin/activate
        echo -e "${GREEN}Virtual environment activated.${NC}"
    fi
}

# Function to deactivate the virtual environment
stop_env() {
    echo -e "${YELLOW}Deactivating virtual environment...${NC}"
    deactivate 2>/dev/null || echo -e "${RED}No active virtual environment found.${NC}"
    echo -e "${GREEN}Virtual environment deactivated.${NC}"
}

# Function to remove the virtual environment
clean_env() {
    echo -e "${YELLOW}Removing virtual environment...${NC}"
    stop_env
    rm -rf ${VENV_PATH}
    echo -e "${GREEN}Virtual environment removed.${NC}"
}

# Function to run the Flask web server
run_server() {
    echo -e "${YELLOW}Starting Flask web server...${NC}"
    start_env
    cd web_controller
    python app.py
}

# Function to run tests
run_tests() {
    echo -e "${YELLOW}Running tests...${NC}"
    start_env
    pytest
}

# Main script logic
case "$1" in
    start)
        start_env
        ;;
    stop)
        stop_env
        ;;
    build)
        build_env
        ;;
    rebuild)
        clean_env
        build_env
        ;;
    clean)
        clean_env
        ;;
    run)
        run_server
        ;;
    test)
        run_tests
        ;;
    help|*)
        show_help
        ;;
esac


