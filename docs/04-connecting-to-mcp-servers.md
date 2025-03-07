# Connecting to MCP Servers

This document explains the different methods for connecting to Model Context Protocol (MCP) servers. Whether you're using Claude Desktop, a custom client, or programmatic access, this guide will help you establish and manage connections to MCP servers.

## Overview of MCP Clients

Before diving into implementation details, it's important to understand what an MCP client does:

1. **Discovers** MCP servers (through configuration or discovery mechanisms)
2. **Establishes** connections to servers using appropriate transport methods
3. **Negotiates** capabilities through protocol initialization
4. **Lists** available tools, resources, and prompts
5. **Facilitates** tool execution, resource retrieval, and prompt application
6. **Handles** errors, timeouts, and reconnection

```mermaid
flowchart LR
    Client[MCP Client]
    Server1[MCP Server 1]
    Server2[MCP Server 2]
    LLM[LLM]
    User[User]
    
    User <--> Client
    Client <--> Server1
    Client <--> Server2
    Client <--> LLM
```

## Client Types

There are several ways to connect to MCP servers:

1. **Integrated Clients**: Built into applications like Claude Desktop
2. **Standalone Clients**: Dedicated applications for MCP interaction (like our Streamlit UI)
3. **SDK Clients**: Using MCP SDKs for programmatic access
4. **Development Tools**: Tools like MCP Inspector for testing and development

## Using Claude Desktop

[Claude Desktop](https://claude.ai/download) is an integrated client that can connect to MCP servers through configuration.

### Configuration Setup

To configure Claude Desktop to use MCP servers:

1. Locate the configuration file:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Create or edit the file to include your MCP servers:

```json
{
  "mcpServers": {
    "web-tools": {
      "command": "python",
      "args": ["/absolute/path/to/server.py"]
    },
    "database-tools": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgres://user:pass@localhost/db"]
    }
  }
}
```

Each server configuration includes:
- A unique name (e.g., "web-tools")
- The command to run the server
- Arguments to pass to the command
- Optional environment variables

### Starting Servers

After configuring Claude Desktop:

1. Restart the application
2. Claude will automatically start configured servers
3. You'll see the MCP tools icon in the interface
4. You can now use the servers in conversations

### Using MCP Features in Claude

With MCP servers configured, you can:

1. **Use tools**: Ask Claude to perform actions using server tools
2. **Access resources**: Request information from resources
3. **Apply prompts**: Use the prompts menu for standardized interactions

## Using the Streamlit UI

The Streamlit UI included in this repository provides a graphical interface for interacting with MCP servers.

### Running the UI

```bash
streamlit run streamlit_app.py
```

This will open a web browser with the UI.

### Connecting to Servers

1. Enter the path to your Claude Desktop config file
2. Click "Load Servers" to see all configured servers
3. Select a server tab and click "Connect"
4. The UI will display tools, resources, and prompts

### Using Tools

1. Select a tool tab
2. Fill in the required parameters
3. Click "Execute" to run the tool
4. View the results in the UI

## Programmatic Access with Python

For programmatic access, you can use the MCP Python SDK.

### Basic Client Example

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def connect_to_server():
    # Set up server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"]
    )
    
    # Connect to the server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # List tools
            tools_result = await session.list_tools()
            print(f"Available tools: {[tool.name for tool in tools_result.tools]}")
            
            # Call a tool
            result = await session.call_tool("web_scrape", {"url": "example.com"})
            print(f"Result: {result.content[0].text if result.content else 'No content'}")

# Run the async function
if __name__ == "__main__":
    asyncio.run(connect_to_server())
```

### Tool Execution

To call a tool programmatically:

```python
# Call a tool with parameters
result = await session.call_tool("tool_name", {
    "param1": "value1",
    "param2": 42
})

# Process the result
if hasattr(result, 'content') and result.content:
    for item in result.content:
        if hasattr(item, 'text'):
            print(item.text)
```

### Resource Access

To access resources programmatically:

```python
# List available resources
resources_result = await session.list_resources()
for resource in resources_result.resources:
    print(f"Resource: {resource.name} ({resource.uri})")

# Read a resource
result = await session.read_resource("resource://uri")
content, mime_type = result.contents[0].text, result.contents[0].mimeType
print(f"Content ({mime_type}): {content[:100]}...")
```

### Prompt Usage

To use prompts programmatically:

```python
# List available prompts
prompts_result = await session.list_prompts()
for prompt in prompts_result.prompts:
    print(f"Prompt: {prompt.name}")

# Get a prompt
result = await session.get_prompt("prompt_name", {"arg1": "value1"})
for message in result.messages:
    print(f"{message.role}: {message.content.text}")
```

## Transport Methods

MCP supports different transport methods for client-server communication.

### STDIO Transport

Standard Input/Output (STDIO) transport is the simplest method:

```python
# STDIO server parameters
server_params = StdioServerParameters(
    command="python",  # Command to run the server
    args=["server.py"],  # Arguments
    env={"ENV_VAR": "value"}  # Optional environment variables
)

# Connect using STDIO
async with stdio_client(server_params) as (read, write):
    # Use the connection...
```

STDIO transport:
- Is simple to set up
- Works well for local processes
- Doesn't require network configuration
- Automatically terminates when the process ends

### SSE Transport

Server-Sent Events (SSE) transport is used for web-based connections:

```python
from mcp.client.sse import sse_client

# Connect to an SSE server
async with sse_client("http://localhost:5000") as (read, write):
    async with ClientSession(read, write) as session:
        # Use the session...
```

SSE transport:
- Supports remote connections
- Works over standard HTTP
- Can be used with web servers
- Supports multiple clients per server

## Connection Lifecycle

Understanding the connection lifecycle is important for robust implementations:

```mermaid
sequenceDiagram
    participant Client
    participant Server
    
    Client->>Server: initialize request
    Server->>Client: initialize response (capabilities)
    Client->>Server: initialized notification
    
    Note over Client,Server: Connection Ready
    
    loop Normal Operation
        Client->>Server: Requests (list_tools, call_tool, etc.)
        Server->>Client: Responses
    end
    
    Note over Client,Server: Termination
    
    Client->>Server: exit notification
    Client->>Server: Close connection
```

### Initialization

When a connection is established:

1. Client sends `initialize` request with supported capabilities
2. Server responds with its capabilities
3. Client sends `initialized` notification
4. Normal operation begins

### Normal Operation

During normal operation:

1. Client sends requests (e.g., `list_tools`, `call_tool`)
2. Server processes requests and sends responses
3. Server may send notifications (e.g., `resources/list_changed`)

### Termination

When ending a connection:

1. Client sends `exit` notification
2. Client closes the connection
3. Server cleans up resources

## Error Handling

Robust error handling is essential for MCP clients:

```python
try:
    result = await session.call_tool("tool_name", params)
except Exception as e:
    print(f"Error calling tool: {str(e)}")
    
    # Check for specific error types
    if isinstance(e, mcp.McpProtocolError):
        print(f"Protocol error: {e.code}")
    elif isinstance(e, mcp.McpTimeoutError):
        print("Request timed out")
    elif isinstance(e, mcp.McpConnectionError):
        print("Connection lost")
```

Common error scenarios:

1. **Connection Failures**: Server not found or refused connection
2. **Initialization Errors**: Protocol incompatibility or capability mismatch
3. **Request Errors**: Invalid parameters or tool not found
4. **Execution Errors**: Tool execution failed or timed out
5. **Connection Loss**: Server terminated unexpectedly

## Building Your Own Client

To build a custom MCP client, follow these steps:

### 1. Set Up Transport

Choose a transport method and establish a connection:

```python
import asyncio
from mcp.client.stdio import stdio_client
from mcp import ClientSession

# Set up server parameters
server_params = StdioServerParameters(
    command="python",
    args=["server.py"]
)

# Establish connection
async with stdio_client(server_params) as (read, write):
    # Create session and use it...
```

### 2. Create a Session

The `ClientSession` manages the protocol interaction:

```python
async with ClientSession(read, write) as session:
    # Initialize the connection
    await session.initialize()
    
    # Now you can use the session
```

### 3. Implement Feature Discovery

List available features from the server:

```python
# List tools
tools_result = await session.list_tools()
tools = tools_result.tools if hasattr(tools_result, 'tools') else []

# List resources
resources_result = await session.list_resources()
resources = resources_result.resources if hasattr(resources_result, 'resources') else []

# List prompts
prompts_result = await session.list_prompts()
prompts = prompts_result.prompts if hasattr(prompts_result, 'prompts') else []
```

### 4. Implement Tool Execution

Create a function to call tools:

```python
async def call_tool(session, tool_name, tool_args):
    try:
        result = await session.call_tool(tool_name, arguments=tool_args)
        
        # Format the result
        if hasattr(result, 'content') and result.content:
            content_text = []
            for item in result.content:
                if hasattr(item, 'text'):
                    content_text.append(item.text)
            return "\n".join(content_text)
        return "Tool executed, but no text content was returned."
    except Exception as e:
        return f"Error calling tool: {str(e)}"
```

### 5. Implement Resource Access

Create a function to read resources:

```python
async def read_resource(session, resource_uri):
    try:
        result = await session.read_resource(resource_uri)
        
        # Format the result
        content_items = []
        for content in result.contents:
            if hasattr(content, 'text'):
                content_items.append(content.text)
            elif hasattr(content, 'blob'):
                content_items.append(f"[Binary data: {len(content.blob)} bytes]")
        
        return "\n".join(content_items)
    except Exception as e:
        return f"Error reading resource: {str(e)}"
```

### 6. Implement User Interface

Create a user interface appropriate for your application:

- Command-line interface
- Web UI (like our Streamlit example)
- GUI application
- Integration with existing tools

## Example: Command-Line Client

Here's a simple command-line client example:

```python
import asyncio
import argparse
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main(args):
    server_params = StdioServerParameters(
        command=args.command,
        args=args.args
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            if args.action == "list-tools":
                tools_result = await session.list_tools()
                tools = tools_result.tools if hasattr(tools_result, 'tools') else []
                print(json.dumps([{
                    "name": tool.name,
                    "description": tool.description
                } for tool in tools], indent=2))
            
            elif args.action == "call-tool":
                tool_args = json.loads(args.params)
                result = await session.call_tool(args.tool, arguments=tool_args)
                if hasattr(result, 'content') and result.content:
                    for item in result.content:
                        if hasattr(item, 'text'):
                            print(item.text)
            
            elif args.action == "list-resources":
                resources_result = await session.list_resources()
                resources = resources_result.resources if hasattr(resources_result, 'resources') else []
                print(json.dumps([{
                    "name": resource.name,
                    "uri": resource.uri
                } for resource in resources], indent=2))
            
            elif args.action == "read-resource":
                result = await session.read_resource(args.uri)
                for content in result.contents:
                    if hasattr(content, 'text'):
                        print(content.text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MCP Command Line Client")
    parser.add_argument("--command", required=True, help="Server command")
    parser.add_argument("--args", nargs="*", default=[], help="Server arguments")
    
    subparsers = parser.add_subparsers(dest="action", required=True)
    
    list_tools_parser = subparsers.add_parser("list-tools")
    
    call_tool_parser = subparsers.add_parser("call-tool")
    call_tool_parser.add_argument("--tool", required=True, help="Tool name")
    call_tool_parser.add_argument("--params", required=True, help="Tool parameters (JSON)")
    
    list_resources_parser = subparsers.add_parser("list-resources")
    
    read_resource_parser = subparsers.add_parser("read-resource")
    read_resource_parser.add_argument("--uri", required=True, help="Resource URI")
    
    args = parser.parse_args()
    asyncio.run(main(args))
```

## Integration with LLMs

To integrate MCP clients with LLMs like Claude:

1. **Tool Registration**: Register MCP tools with the LLM system
2. **Resource Loading**: Provide a way to load resources into LLM context
3. **Permission Handling**: Implement approval flows for tool execution
4. **Result Processing**: Process and present tool results to the LLM

Example integration with Anthropic Claude:

```python
import anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def process_claude_query(client, query):
    # Connect to MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()
            
            # Get available tools
            tools_result = await session.list_tools()
            tools = []
            for tool in tools_result.tools:
                tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                })
            
            # Initial Claude query
            messages = [{"role": "user", "content": query}]
            response = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                messages=messages,
                tools=tools
            )
            
            # Process tool calls
            for content in response.content:
                if content.type == "tool_use":
                    # Execute the tool
                    tool_name = content.name
                    tool_args = content.input
                    
                    # Call MCP tool
                    result = await session.call_tool(tool_name, arguments=tool_args)
                    
                    # Format result
                    result_text = ""
                    if hasattr(result, 'content') and result.content:
                        for item in result.content:
                            if hasattr(item, 'text'):
                                result_text += item.text
                    
                    # Send result back to Claude
                    messages.append({
                        "role": "assistant",
                        "content": [content]
                    })
                    messages.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": content.id,
                                "content": result_text
                            }
                        ]
                    })
                    
                    # Get final response
                    final_response = client.messages.create(
                        model="claude-3-opus-20240229",
                        max_tokens=1000,
                        messages=messages
                    )
                    
                    return final_response.content[0].text
            
            # If no tool calls, return initial response
            return response.content[0].text
```

## Troubleshooting Connection Issues

### Common Problems and Solutions

1. **Server Not Found**:
   - Check that the command path is correct
   - Verify the server file exists
   - Check that Python or Node.js is properly installed

2. **Connection Refused**:
   - For SSE, verify the port is available
   - Check for firewall or network issues
   - Ensure the server is running

3. **Protocol Errors**:
   - Verify MCP versions are compatible
   - Check for syntax errors in tool schemas
   - Ensure tools are properly registered

4. **Tool Execution Failures**:
   - Validate input parameters
   - Check for runtime errors in tool implementation
   - Verify external dependencies are available

5. **Node.js Environment Issues**:
   - Ensure Node.js is properly installed
   - Check for proper paths to node, npm, and npx
   - Verify global packages are accessible

### Debugging Techniques

1. **Logging**:
   - Enable debug logging in your client
   - Check server logs for errors
   - Use the MCP Inspector for detailed message logs

2. **Environment Variables**:
   - Set `MCP_DEBUG=1` for verbose logging
   - Use appropriate environment variables for servers

3. **Manual Testing**:
   - Test servers directly with the MCP Inspector
   - Try simple tools first to isolate issues
   - Verify transport works with echo tools

## Conclusion

Connecting to MCP servers opens up powerful capabilities for extending LLMs with custom tools and data sources. Whether using existing clients like Claude Desktop, building custom integrations, or developing your own applications, the MCP protocol provides a standardized way to enhance LLM interactions.

In the next document, we'll explore the communication protocols used by MCP in more detail.
