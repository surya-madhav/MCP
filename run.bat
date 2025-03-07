@echo off
REM Script to run either the MCP server or the Streamlit UI

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in your PATH. Please install Python first.
    exit /b 1
)

REM Check if pip is installed
where pip >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo pip is not installed or not in your PATH. Please install pip first.
    exit /b 1
)

REM Function to check and install dependencies
:check_dependencies
    echo Checking dependencies...
    
    REM Check if requirements.txt exists
    if not exist "requirements.txt" (
        echo requirements.txt not found. Please run this script from the repository root.
        exit /b 1
    )
    
    REM Install dependencies
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
    
    if %ERRORLEVEL% neq 0 (
        echo Failed to install dependencies. Please check the errors above.
        exit /b 1
    )
    
    echo Dependencies installed successfully.
    exit /b 0

REM Function to run the MCP server
:run_server
    echo Starting MCP server...
    echo Press Ctrl+C to stop the server.
    python server.py %*
    exit /b 0

REM Function to run the Streamlit UI
:run_ui
    echo Starting Streamlit UI...
    echo Press Ctrl+C to stop the UI.
    streamlit run streamlit_app.py
    exit /b 0

REM Main script
if "%1"=="server" (
    call :check_dependencies
    if %ERRORLEVEL% neq 0 exit /b 1
    shift
    call :run_server %*
) else if "%1"=="ui" (
    call :check_dependencies
    if %ERRORLEVEL% neq 0 exit /b 1
    call :run_ui
) else (
    echo MCP Tools Runner
    echo Usage:
    echo   run.bat server [args]  - Run the MCP server with optional arguments
    echo   run.bat ui             - Run the Streamlit UI
    echo.
    echo Examples:
    echo   run.bat server                        - Run the server with stdio transport
    echo   run.bat server --transport sse        - Run the server with SSE transport
    echo   run.bat ui                            - Start the Streamlit UI
)
