#!/bin/bash
# Script to run either the MCP server or the Streamlit UI

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python &> /dev/null
then
    echo -e "${RED}Python is not installed or not in your PATH. Please install Python first.${NC}"
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null
then
    echo -e "${RED}pip is not installed or not in your PATH. Please install pip first.${NC}"
    exit 1
fi

# Function to check and install dependencies
check_dependencies() {
    echo -e "${BLUE}Checking dependencies...${NC}"
    
    # Check if requirements.txt exists
    if [ ! -f "requirements.txt" ]; then
        echo -e "${RED}requirements.txt not found. Please run this script from the repository root.${NC}"
        exit 1
    fi
    
    # Install dependencies
    echo -e "${YELLOW}Installing dependencies from requirements.txt...${NC}"
    pip install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install dependencies. Please check the errors above.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Dependencies installed successfully.${NC}"
}

# Function to run the MCP server
run_server() {
    echo -e "${BLUE}Starting MCP server...${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop the server.${NC}"
    python server.py "$@"
}

# Function to run the Streamlit UI
run_ui() {
    echo -e "${BLUE}Starting MCP Dev Tools UI...${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop the UI.${NC}"
    # Use the new frontend/app.py file instead of app.py
    streamlit run frontend/app.py
}

# Main script
case "$1" in
    server)
        shift # Remove the first argument
        check_dependencies
        run_server "$@"
        ;;
    ui)
        check_dependencies
        run_ui
        ;;
    *)
        echo -e "${BLUE}MCP Dev Tools Runner${NC}"
        echo -e "${YELLOW}Usage:${NC}"
        echo -e "  ./run.sh server [args]  - Run the MCP server with optional arguments"
        echo -e "  ./run.sh ui             - Run the MCP Dev Tools UI"
        echo
        echo -e "${YELLOW}Examples:${NC}"
        echo -e "  ./run.sh server                        - Run the server with stdio transport"
        echo -e "  ./run.sh server --transport sse        - Run the server with SSE transport"
        echo -e "  ./run.sh ui                            - Start the MCP Dev Tools UI"
        ;;
esac
