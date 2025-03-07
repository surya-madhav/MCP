# Building MCP Servers with Python

This guide provides a comprehensive walkthrough for building Model Context Protocol (MCP) servers using Python. We'll cover everything from basic setup to advanced techniques, with practical examples and best practices.

## Prerequisites

Before starting, ensure you have:

- Python 3.10 or higher installed
- Basic knowledge of Python and async programming
- Understanding of MCP core concepts (tools, resources, prompts)
- A development environment with your preferred code editor

## Setting Up Your Environment

### Installation

Start by creating a virtual environment and installing the MCP package:

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install MCP
pip install mcp
```

Alternatively, if you're using [uv](https://github.com/astral-sh/uv) for package management:

```bash
# Create a virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install MCP
uv pip install mcp
```

### Project Structure

A well-organized MCP server project typically follows this structure:

```
my-mcp-server/
├── requirements.txt
├── server.py
├── tools/
│   ├── __init__.py
│   ├── tool_module1.py
│   └── tool_module2.py
├── resources/
│   ├── __init__.py
│   └── resource_modules.py
└── prompts/
    ├── __init__.py
    └── prompt_modules.py
```

This modular structure keeps your code organized and makes it easier to add new functionality over time.

## Creating Your First MCP Server

### Basic Server Structure

Let's create a simple MCP server with a "hello world" tool:

```python
# server.py
from mcp.server.fastmcp import FastMCP

# Create a server
mcp = FastMCP("HelloWorld")

@mcp.tool()
def hello(name: str = "World") -> str:
    """
    Say hello to a name.
    
    Args:
        name: The name to greet (default: "World")
    
    Returns:
        A greeting message
    """
    return f"Hello, {name}!"

if __name__ == "__main__":
    # Run the server
    mcp.run()
```

This basic server:
1. Creates a FastMCP server named "HelloWorld"
2. Defines a simple tool called "hello" that takes a name parameter
3. Runs the server using the default stdio transport

### Running Your Server

To run your server:

```bash
python server.py
```

The server will start and wait for connections on the standard input/output streams.

### FastMCP vs. Low-Level API

The MCP Python SDK provides two ways to create servers:

1. **FastMCP**: A high-level API that simplifies server creation through decorators
2. **Low-Level API**: Provides more control but requires more boilerplate code

Most developers should start with FastMCP, as it handles many details automatically.

## Implementing Tools

Tools are the most common primitive in MCP servers. They allow LLMs to perform actions and retrieve information.

### Basic Tool Example

Here's how to implement a simple calculator tool:

```python
@mcp.tool()
def calculate(operation: str, a: float, b: float) -> float:
    """
    Perform basic arithmetic operations.
    
    Args:
        operation: The operation to perform (add, subtract, multiply, divide)
        a: First number
        b: Second number
    
    Returns:
        The result of the operation
    """
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    else:
        raise ValueError(f"Unknown operation: {operation}")
```

### Asynchronous Tools

For operations that involve I/O or might take time, use async tools:

```python
@mcp.tool()
async def fetch_weather(city: str) -> str:
    """
    Fetch weather information for a city.
    
    Args:
        city: The city name
    
    Returns:
        Weather information
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://weather-api.example.com/{city}")
        data = response.json()
        return f"Temperature: {data['temp']}°C, Conditions: {data['conditions']}"
```

### Tool Parameters

Tools can have:

- Required parameters
- Optional parameters with defaults
- Type hints that are used to generate schema
- Docstrings that provide descriptions

```python
@mcp.tool()
def search_database(
    query: str,
    limit: int = 10,
    offset: int = 0,
    sort_by: str = "relevance"
) -> list:
    """
    Search the database for records matching the query.
    
    Args:
        query: The search query string
        limit: Maximum number of results to return (default: 10)
        offset: Number of results to skip (default: 0)
        sort_by: Field to sort results by (default: "relevance")
    
    Returns:
        List of matching records
    """
    # Implementation details...
    return results
```

### Error Handling in Tools

Proper error handling is essential for robust tools:

```python
@mcp.tool()
def divide(a: float, b: float) -> float:
    """
    Divide two numbers.
    
    Args:
        a: Numerator
        b: Denominator
    
    Returns:
        The division result
    
    Raises:
        ValueError: If attempting to divide by zero
    """
    try:
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    except Exception as e:
        # Log the error for debugging
        logging.error(f"Error in divide tool: {str(e)}")
        # Re-raise with a user-friendly message
        raise ValueError(f"Division failed: {str(e)}")
```

### Grouping Related Tools

For complex servers, organize related tools into modules:

```python
# tools/math_tools.py
def register_math_tools(mcp):
    @mcp.tool()
    def add(a: float, b: float) -> float:
        """Add two numbers."""
        return a + b
    
    @mcp.tool()
    def subtract(a: float, b: float) -> float:
        """Subtract b from a."""
        return a - b
    
    # More math tools...

# server.py
from tools.math_tools import register_math_tools

mcp = FastMCP("MathServer")
register_math_tools(mcp)
```

## Implementing Resources

Resources provide data to LLMs through URI-based access patterns.

### Basic Resource Example

Here's a simple file resource:

```python
@mcp.resource("file://{path}")
async def get_file(path: str) -> str:
    """
    Get the content of a file.
    
    Args:
        path: Path to the file
    
    Returns:
        The file content
    """
    try:
        async with aiofiles.open(path, "r") as f:
            return await f.read()
    except Exception as e:
        raise ValueError(f"Failed to read file: {str(e)}")
```

### Dynamic Resources

Resources can be dynamic and parameterized:

```python
@mcp.resource("database://{table}/{id}")
async def get_database_record(table: str, id: str) -> str:
    """
    Get a record from the database.
    
    Args:
        table: The table name
        id: The record ID
    
    Returns:
        The record data
    """
    # Implementation details...
    return json.dumps(record)
```

### Resource Metadata

Resources can include metadata:

```python
@mcp.resource("api://{endpoint}")
async def get_api_data(endpoint: str) -> tuple:
    """
    Get data from an API endpoint.
    
    Args:
        endpoint: The API endpoint path
    
    Returns:
        A tuple of (content, mime_type)
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com/{endpoint}")
        return response.text, response.headers.get("content-type", "text/plain")
```

### Binary Resources

Resources can return binary data:

```python
from mcp.server.fastmcp import Image

@mcp.resource("image://{path}")
async def get_image(path: str) -> Image:
    """
    Get an image file.
    
    Args:
        path: Path to the image
    
    Returns:
        The image data
    """
    with open(path, "rb") as f:
        data = f.read()
    return Image(data=data, format=path.split(".")[-1])
```

## Implementing Prompts

Prompts are templates that help LLMs interact with your server effectively.

### Basic Prompt Example

Here's a simple query prompt:

```python
@mcp.prompt()
def search_query(query: str) -> str:
    """
    Create a search query prompt.
    
    Args:
        query: The search query
    
    Returns:
        Formatted search query prompt
    """
    return f"""
    Please search for information about:
    
    {query}
    
    Focus on the most relevant and up-to-date information.
    """
```

### Multi-Message Prompts

Prompts can include multiple messages:

```python
from mcp.types import UserMessage, AssistantMessage

@mcp.prompt()
def debug_error(error: str) -> list:
    """
    Create a debugging conversation.
    
    Args:
        error: The error message
    
    Returns:
        A list of messages
    """
    return [
        UserMessage(f"I'm getting this error: {error}"),
        AssistantMessage("Let me help debug that. What have you tried so far?")
    ]
```

## Transport Options

MCP supports different transport mechanisms for communication between clients and servers.

### STDIO Transport (Default)

The default transport uses standard input/output streams:

```python
if __name__ == "__main__":
    mcp.run(transport="stdio")
```

This is ideal for local processes and command-line tools.

### SSE Transport

Server-Sent Events (SSE) transport is used for web applications:

```python
if __name__ == "__main__":
    mcp.run(transport="sse", host="localhost", port=5000)
```

This starts an HTTP server that accepts MCP connections through SSE.

## Context and Lifespan

### Using Context

The `Context` object provides access to the current request context:

```python
from mcp.server.fastmcp import Context

@mcp.tool()
async def log_message(message: str, ctx: Context) -> str:
    """
    Log a message and return a confirmation.
    
    Args:
        message: The message to log
        ctx: The request context
    
    Returns:
        Confirmation message
    """
    ctx.info(f"User logged: {message}")
    return f"Message logged: {message}"
```

### Progress Reporting

For long-running tools, report progress:

```python
@mcp.tool()
async def process_files(files: list[str], ctx: Context) -> str:
    """
    Process multiple files with progress tracking.
    
    Args:
        files: List of file paths
        ctx: The request context
    
    Returns:
        Processing summary
    """
    total = len(files)
    for i, file in enumerate(files):
        # Report progress (0-100%)
        await ctx.report_progress(i * 100 // total)
        # Process the file...
        ctx.info(f"Processing {file}")
    
    return f"Processed {total} files"
```

### Lifespan Management

For servers that need initialization and cleanup:

```python
from contextlib import asynccontextmanager
from typing import AsyncIterator

@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[dict]:
    """Manage server lifecycle."""
    # Setup (runs on startup)
    db = await Database.connect()
    try:
        yield {"db": db}  # Pass context to handlers
    finally:
        # Cleanup (runs on shutdown)
        await db.disconnect()

# Create server with lifespan
mcp = FastMCP("DatabaseServer", lifespan=lifespan)

@mcp.tool()
async def query_db(sql: str, ctx: Context) -> list:
    """Run a database query."""
    db = ctx.request_context.lifespan_context["db"]
    return await db.execute(sql)
```

## Testing MCP Servers

### Using the MCP Inspector

The MCP Inspector is a tool for testing MCP servers:

```bash
# Install the inspector
npm install -g @modelcontextprotocol/inspector

# Run your server with the inspector
npx @modelcontextprotocol/inspector python server.py
```

This opens a web interface where you can:
- See available tools, resources, and prompts
- Test tools with different parameters
- View tool execution results
- Explore resource content

### Manual Testing

You can also test your server programmatically:

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_server():
    # Connect to the server
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # List tools
            tools = await session.list_tools()
            print(f"Available tools: {[tool.name for tool in tools.tools]}")
            
            # Call a tool
            result = await session.call_tool("hello", {"name": "MCP"})
            print(f"Tool result: {result.content[0].text}")

if __name__ == "__main__":
    asyncio.run(test_server())
```

## Debugging MCP Servers

### Logging

Use logging to debug your server:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Access the MCP logger
logger = logging.getLogger("mcp")
```

### Common Issues

1. **Schema Generation**:
   - Ensure type hints are accurate
   - Provide docstrings for tools
   - Check parameter names and types

2. **Async/Sync Mismatch**:
   - Use `async def` for tools that use async operations
   - Don't mix async and sync code without proper handling

3. **Transport Issues**:
   - Check that stdio is not mixed with print statements
   - Ensure ports are available for SSE transport
   - Verify network settings for remote connections

## Deployment Options

### Local Deployment

For local use with Claude Desktop:

1. Edit the Claude Desktop config file:
   ```json
   {
     "mcpServers": {
       "my-server": {
         "command": "python",
         "args": ["/path/to/server.py"]
       }
     }
   }
   ```

2. Restart Claude Desktop

### Web Deployment

For web deployment with SSE transport:

1. Set up a web server (e.g., nginx) to proxy requests
2. Use a process manager (e.g., systemd, supervisor) to keep the server running
3. Configure the server to use SSE transport with appropriate host/port

Example systemd service:

```ini
[Unit]
Description=MCP Server
After=network.target

[Service]
User=mcp
WorkingDirectory=/path/to/server
ExecStart=/path/to/venv/bin/python server.py --transport sse --host 127.0.0.1 --port 5000
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

## Security Considerations

When building MCP servers, consider these security aspects:

1. **Input Validation**:
   - Validate all parameters
   - Sanitize file paths and system commands
   - Use allowlists for sensitive operations

2. **Resource Access**:
   - Limit access to specific directories
   - Avoid exposing sensitive information
   - Use proper permissions for files

3. **Error Handling**:
   - Don't expose internal errors to clients
   - Log security-relevant errors
   - Implement proper error recovery

4. **Authentication**:
   - Implement authentication for sensitive operations
   - Use secure tokens or credentials
   - Verify client identity when needed

## Example: Web Scraping Server

Let's build a complete web scraping server that fetches and returns content from URLs:

```python
# server.py
import httpx
from mcp.server.fastmcp import FastMCP

# Create the server
mcp = FastMCP("WebScraper")

@mcp.tool()
async def web_scrape(url: str) -> str:
    """
    Fetch content from a URL and return it.
    
    Args:
        url: The URL to scrape
    
    Returns:
        The page content
    """
    # Ensure URL has a scheme
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Fetch the content
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            return response.text
    except httpx.HTTPStatusError as e:
        return f"Error: HTTP status error - {e.response.status_code}"
    except httpx.RequestError as e:
        return f"Error: Request failed - {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error occurred - {str(e)}"

if __name__ == "__main__":
    mcp.run()
```

## Conclusion

Building MCP servers with Python is a powerful way to extend LLM capabilities. By following the patterns and practices in this guide, you can create robust, maintainable MCP servers that integrate with Claude and other LLMs.

In the next document, we'll explore how to connect to MCP servers from different clients.
