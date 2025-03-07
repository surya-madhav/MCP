# MCP Troubleshooting Guide

This comprehensive guide addresses common issues encountered when working with Model Context Protocol (MCP) servers and clients. It provides step-by-step solutions, diagnostic techniques, and best practices for resolving problems efficiently.

## Environment Setup Issues

### Python Environment Problems

#### Missing Dependencies

**Symptoms:**
- Import errors when running server code
- "Module not found" errors
- Unexpected version conflicts

**Solutions:**
1. Verify all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Check for version conflicts:
   ```bash
   pip list
   ```

3. Consider using a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. Try using `uv` for faster, more reliable installation:
   ```bash
   uv pip install -r requirements.txt
   ```

#### Incompatible Python Version

**Symptoms:**
- Syntax errors in valid code
- Feature not found errors
- Type hint errors

**Solutions:**
1. Check your Python version:
   ```bash
   python --version
   ```

2. Ensure you're using Python 3.10 or higher (required for MCP):
   ```bash
   # Install or update Python if needed
   # Then create a new virtual environment with the correct version
   python3.10 -m venv venv
   ```

### Node.js Environment Problems

#### Missing or Inaccessible Node.js

**Symptoms:**
- "Command not found: npx" errors
- "npx is not recognized as an internal or external command"
- Node.js servers fail to start

**Solutions:**
1. Verify Node.js installation:
   ```bash
   node --version
   npm --version
   npx --version
   ```

2. Install Node.js if needed (from [nodejs.org](https://nodejs.org/))

3. Check PATH environment variable:
   ```bash
   # On Unix-like systems
   echo $PATH
   
   # On Windows
   echo %PATH%
   ```

4. Find the location of Node.js binaries:
   ```bash
   # On Unix-like systems
   which node
   which npm
   which npx
   
   # On Windows
   where node
   where npm
   where npx
   ```

5. Add the Node.js bin directory to your PATH if needed

#### NPM Package Issues

**Symptoms:**
- NPM packages fail to install
- "Error: Cannot find module" when using npx
- Permission errors during installation

**Solutions:**
1. Clear npm cache:
   ```bash
   npm cache clean --force
   ```

2. Try installing packages globally:
   ```bash
   npm install -g @modelcontextprotocol/server-name
   ```

3. Check npm permissions:
   ```bash
   # Fix ownership issues on Unix-like systems
   sudo chown -R $(whoami) ~/.npm
   ```

4. Use npx with explicit paths:
   ```bash
   npx --no-install @modelcontextprotocol/server-name
   ```

## Server Connection Issues

### STDIO Connection Problems

#### Process Launch Failures

**Symptoms:**
- "No such file or directory" errors
- "Cannot execute binary file" errors
- Process exits immediately

**Solutions:**
1. Check that the command exists and is executable:
   ```bash
   # For Python servers
   which python
   
   # For Node.js servers
   which node
   ```

2. Verify file paths are correct:
   ```bash
   # Check if file exists
   ls -l /path/to/server.py
   ```

3. Use absolute paths in configuration:
   ```json
   {
     "command": "/usr/bin/python",
     "args": ["/absolute/path/to/server.py"]
   }
   ```

4. Check file permissions:
   ```bash
   # Make script executable if needed
   chmod +x /path/to/server.py
   ```

#### STDIO Protocol Errors

**Symptoms:**
- "Unexpected message format" errors
- "Invalid JSON" errors
- Connection dropped after initialization

**Solutions:**
1. Avoid mixing regular print statements with MCP protocol:
   ```python
   # Bad: writes to stdout, interfering with protocol
   print("Debug info")
   
   # Good: writes to stderr, doesn't interfere
   import sys
   print("Debug info", file=sys.stderr)
   ```

2. Enable protocol logging for debugging:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

3. Check for blocked I/O operations

### SSE Connection Problems

#### HTTP Server Issues

**Symptoms:**
- "Connection refused" errors
- Timeout errors
- SSE connection fails

**Solutions:**
1. Verify server is running on the correct host/port:
   ```bash
   # Check if something is listening on the port
   netstat -tuln | grep 5000
   ```

2. Check for firewall or network issues:
   ```bash
   # Test connection to server
   curl http://localhost:5000/
   ```

3. Ensure CORS is properly configured (for web clients):
   ```python
   # Example CORS headers in aiohttp
   response.headers.update({
       'Access-Control-Allow-Origin': '*',
       'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
       'Access-Control-Allow-Headers': 'Content-Type'
   })
   ```

#### SSE Message Problems

**Symptoms:**
- Messages not received
- "Invalid SSE format" errors
- Connection closes unexpectedly

**Solutions:**
1. Check SSE message format:
   ```
   event: message
   data: {"jsonrpc":"2.0","id":1,"result":{...}}
   
   ```
   (Note the double newline at the end)

2. Verify content-type header:
   ```
   Content-Type: text/event-stream
   ```

3. Ensure Keep-Alive is properly configured:
   ```
   Connection: keep-alive
   Cache-Control: no-cache
   ```

## Claude Desktop Integration Issues

### Configuration Problems

#### Configuration File Issues

**Symptoms:**
- MCP servers don't appear in Claude
- "Failed to start server" errors
- No MCP icon in Claude interface

**Solutions:**
1. Check configuration file location:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Verify JSON syntax is valid:
   ```json
   {
     "mcpServers": {
       "web-tools": {
         "command": "python",
         "args": ["/absolute/path/to/server.py"]
       }
     }
   }
   ```

3. Create the file if it doesn't exist:
   ```bash
   # Create directory if needed
   mkdir -p ~/Library/Application\ Support/Claude/
   
   # Create basic config file
   echo '{"mcpServers":{}}' > ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

4. Check file permissions:
   ```bash
   # Ensure user can read/write the file
   chmod 600 ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

#### Server Path Issues

**Symptoms:**
- "Command not found" errors
- "No such file or directory" errors

**Solutions:**
1. Use absolute paths in configuration:
   ```json
   {
     "mcpServers": {
       "web-tools": {
         "command": "/usr/bin/python",
         "args": ["/Users/username/Documents/Personal/MCP/server.py"]
       }
     }
   }
   ```

2. Avoid using environment variables or relative paths:
   ```json
   // Bad: using relative path
   "args": ["./server.py"]
   
   // Good: using absolute path
   "args": ["/Users/username/Documents/Personal/MCP/server.py"]
   ```

3. Escape backslashes properly on Windows:
   ```json
   "args": ["C:\\Users\\username\\Documents\\Personal\\MCP\\server.py"]
   ```

### Tool Execution Problems

#### Permission Denials

**Symptoms:**
- "Permission denied" errors
- Tools fail silently
- Claude cannot access files or resources

**Solutions:**
1. Check file and directory permissions:
   ```bash
   ls -la /path/to/files/
   ```

2. Run Claude Desktop with appropriate permissions

3. Check for sandboxing restrictions

#### Command Execution Failures

**Symptoms:**
- Tools fail but not due to permission issues
- Timeouts during tool execution
- Tool returns error message

**Solutions:**
1. Check logs for detailed error messages:
   ```bash
   # View Claude Desktop MCP logs
   tail -f ~/Library/Logs/Claude/mcp*.log
   ```

2. Test tools directly outside of Claude:
   ```bash
   # Run the server directly and test with MCP Inspector
   npx @modelcontextprotocol/inspector python server.py
   ```

3. Implement better error handling in tools

## Streamlit UI Issues

### Connection Problems

#### Config File Access

**Symptoms:**
- "File not found" errors
- Cannot load servers from config file
- Permission errors

**Solutions:**
1. Verify the config file path is correct
2. Check file permissions
3. Use the pre-filled default path if available

#### Server Command Execution

**Symptoms:**
- "Command not found" errors
- Node.js/Python not found
- Server fails to start

**Solutions:**
1. Check environment detection in the UI:
   ```python
   # Are Node.js and other tools detected?
   node_installed = bool(find_executable('node'))
   ```

2. Add logging to track command execution:
   ```python
   print(f"Trying to execute: {command} {' '.join(args)}")
   ```

3. Use full paths to executables

### UI Display Issues

#### Tool Schema Problems

**Symptoms:**
- Tool parameters not displayed correctly
- Input fields missing
- Form submission fails

**Solutions:**
1. Check tool schema format:
   ```python
   # Ensure schema has proper structure
   @mcp.tool()
   def my_tool(param1: str, param2: int = 0) -> str:
       """
       Tool description.
       
       Args:
           param1: Description of param1
           param2: Description of param2 (default: 0)
       
       Returns:
           Result description
       """
       # Implementation
   ```

2. Verify all required schema fields are present
3. Check for type conversion issues

#### Tool Execution Display

**Symptoms:**
- Results not displayed
- Format issues in results
- Truncated output

**Solutions:**
1. Check error handling in result processing:
   ```python
   try:
       result = asyncio.run(call_tool(command, args, tool_name, tool_inputs))
       st.subheader("Result")
       st.write(result)
   except Exception as e:
       st.error(f"Error: {str(e)}")
   ```

2. Improve content type handling:
   ```python
   # Process different content types
   for item in result.content:
       if hasattr(item, 'text'):
           st.write(item.text)
       elif hasattr(item, 'blob'):
           st.write("Binary data: use appropriate display method")
   ```

3. Add pagination for large results

## Tool-Specific Issues

### Web Scraping Tool Problems

#### URL Formatting Issues

**Symptoms:**
- "Invalid URL" errors
- Requests to wrong domain
- URL protocol issues

**Solutions:**
1. Ensure proper URL formatting:
   ```python
   # Add protocol if missing
   if not url.startswith(('http://', 'https://')):
       url = 'https://' + url
   ```

2. Handle URL encoding properly:
   ```python
   from urllib.parse import quote_plus
   
   # Encode URL components
   safe_url = quote_plus(url)
   ```

3. Validate URLs before processing:
   ```python
   import re
   
   # Simple URL validation
   if not re.match(r'^(https?://)?[a-zA-Z0-9][-a-zA-Z0-9.]*\.[a-zA-Z]{2,}(/.*)?$', url):
       raise ValueError("Invalid URL format")
   ```

#### HTTP Request Failures

**Symptoms:**
- Timeouts
- Rate limiting errors
- Connection refused errors

**Solutions:**
1. Implement proper error handling:
   ```python
   try:
       async with httpx.AsyncClient() as client:
           response = await client.get(url, timeout=30.0)
           response.raise_for_status()
           return response.text
   except httpx.HTTPStatusError as e:
       return f"Error: HTTP status error - {e.response.status_code}"
   except httpx.RequestError as e:
       return f"Error: Request failed - {str(e)}"
   ```

2. Add retries for transient errors:
   ```python
   for attempt in range(3):
       try:
           async with httpx.AsyncClient() as client:
               response = await client.get(url, timeout=30.0)
               response.raise_for_status()
               return response.text
       except (httpx.HTTPStatusError, httpx.RequestError) as e:
           if attempt == 2:  # Last attempt
               raise
           await asyncio.sleep(1)  # Wait before retry
   ```

3. Add user-agent headers:
   ```python
   headers = {
       "User-Agent": "MCP-WebScraper/1.0",
       "Accept": "text/html,application/xhtml+xml,application/xml"
   }
   response = await client.get(url, headers=headers, timeout=30.0)
   ```

#### Content Processing Issues

**Symptoms:**
- Empty or malformed content
- Encoding issues
- Content too large

**Solutions:**
1. Handle different content types:
   ```python
   if "application/json" in response.headers.get("content-type", ""):
       return json.dumps(response.json(), indent=2)
   elif "text/html" in response.headers.get("content-type", ""):
       # Extract main content
       soup = BeautifulSoup(response.text, 'html.parser')
       # Remove scripts, styles, etc.
       for script in soup(["script", "style", "meta", "noscript"]):
           script.extract()
       return soup.get_text()
   else:
       return response.text
   ```

2. Handle encoding properly:
   ```python
   # Detect encoding
   encoding = response.encoding
   # Fix common encoding issues
   if not encoding or encoding == 'ISO-8859-1':
       encoding = 'utf-8'
   text = response.content.decode(encoding, errors='replace')
   ```

3. Implement content size limits:
   ```python
   # Limit content size
   max_size = 100 * 1024  # 100 KB
   if len(response.content) > max_size:
       return response.content[:max_size].decode('utf-8', errors='replace') + "\n[Content truncated...]"
   ```

## Protocol and Message Issues

### JSON-RPC Issues

#### Invalid Message Format

**Symptoms:**
- "Invalid request" errors
- "Parse error" errors
- Unexpected protocol errors

**Solutions:**
1. Validate JSON-RPC message structure:
   ```python
   def validate_jsonrpc_message(message):
       if "jsonrpc" not in message or message["jsonrpc"] != "2.0":
           raise ValueError("Invalid jsonrpc version")
       
       if "method" in message:
           if "id" in message:
               # It's a request
               if "params" in message and not isinstance(message["params"], (dict, list)):
                   raise ValueError("Params must be object or array")
           else:
               # It's a notification
               pass
       elif "id" in message:
           # It's a response
           if "result" not in message and "error" not in message:
               raise ValueError("Response must have result or error")
           if "error" in message and "result" in message:
               raise ValueError("Response cannot have both result and error")
       else:
           raise ValueError("Invalid message format")
   ```

2. Use proper JSON-RPC libraries:
   ```python
   from jsonrpcserver import method, async_dispatch
   from jsonrpcclient import request, parse
   ```

3. Check for JSON encoding/decoding issues:
   ```python
   try:
       json_str = json.dumps(message)
       decoded = json.loads(json_str)
       # Compare decoded with original to check for precision loss
   except Exception as e:
       print(f"JSON error: {str(e)}")
   ```

#### Method Not Found

**Symptoms:**
- "Method not found" errors
- Methods available but not accessible
- Methods incorrectly implemented

**Solutions:**
1. Check method registration:
   ```python
   # For FastMCP, ensure methods are properly decorated
   @mcp.tool()
   def my_tool():
       pass
       
   # For low-level API, ensure methods are registered
   server.setRequestHandler("tools/call", handle_tool_call)
   ```

2. Verify method names exactly match specifications:
   ```
   tools/list
   tools/call
   resources/list
   resources/read
   prompts/list
   prompts/get
   ```

3. Check capability negotiation:
   ```python
   # Ensure capabilities are properly declared
   server = FastMCP(
       "MyServer",
       capabilities={
           "tools": {
               "listChanged": True
           }
       }
   )
   ```

### Error Handling Issues

#### Unhandled Exceptions

**Symptoms:**
- Crashes during operation
- Unexpected termination
- Missing error responses

**Solutions:**
1. Wrap operations in try-except blocks:
   ```python
   @mcp.tool()
   async def risky_operation(param: str) -> str:
       try:
           # Potentially dangerous operation
           result = await perform_operation(param)
           return result
       except Exception as e:
           # Log the error
           logging.error(f"Error in risky_operation: {str(e)}")
           # Return a friendly error message
           return f"Operation failed: {str(e)}"
   ```

2. Use context managers for resource cleanup:
   ```python
   @mcp.tool()
   async def file_operation(path: str) -> str:
       try:
           async with aiofiles.open(path, "r") as f:
               content = await f.read()
           return content
       except FileNotFoundError:
           return f"File not found: {path}"
       except PermissionError:
           return f"Permission denied: {path}"
       except Exception as e:
           return f"Error reading file: {str(e)}"
   ```

3. Implement proper error responses:
   ```python
   # Return error in tool result
   return {
       "isError": True,
       "content": [
           {
               "type": "text",
               "text": f"Error: {str(e)}"
           }
       ]
   }
   ```

#### Error Response Format

**Symptoms:**
- Clients can't parse error responses
- Errors not displayed properly
- Missing error details

**Solutions:**
1. Use standard error codes:
   ```python
   # JSON-RPC standard error codes
   PARSE_ERROR = -32700
   INVALID_REQUEST = -32600
   METHOD_NOT_FOUND = -32601
   INVALID_PARAMS = -32602
   INTERNAL_ERROR = -32603
   
   # MCP-specific error codes
   RESOURCE_NOT_FOUND = -32001
   TOOL_NOT_FOUND = -32002
   PROMPT_NOT_FOUND = -32003
   EXECUTION_FAILED = -32004
   ```

2. Include helpful error messages:
   ```python
   raise McpError(
       code=INVALID_PARAMS,
       message="Invalid parameters",
       data={
           "details": "Parameter 'url' must be a valid URL",
           "parameter": "url"
       }
   )
   ```

3. Log detailed errors but return simplified messages:
   ```python
   try:
       # Operation
   except Exception as e:
       # Log detailed error
       logging.error(f"Detailed error: {str(e)}", exc_info=True)
       # Return simplified error to client
       raise McpError(
           code=INTERNAL_ERROR,
           message="Operation failed"
       )
   ```

## Advanced Troubleshooting Techniques

### Logging and Monitoring

#### Setting Up Comprehensive Logging

**Approach:**
1. Configure logging at different levels:
   ```python
   import logging
   
   # Set up file handler
   file_handler = logging.FileHandler("mcp_server.log")
   file_handler.setLevel(logging.DEBUG)
   
   # Set up console handler
   console_handler = logging.StreamHandler()
   console_handler.setLevel(logging.INFO)
   
   # Set up formatter
   formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
   file_handler.setFormatter(formatter)
   console_handler.setFormatter(formatter)
   
   # Configure logger
   logger = logging.getLogger("mcp")
   logger.setLevel(logging.DEBUG)
   logger.addHandler(file_handler)
   logger.addHandler(console_handler)
   ```

2. Log at appropriate levels:
   ```python
   logger.debug("Detailed debug info")
   logger.info("General operational info")
   logger.warning("Warning - something unexpected")
   logger.error("Error - operation failed")
   logger.critical("Critical - system failure")
   ```

3. Use structured logging for better analysis:
   ```python
   import json
   
   def log_structured(level, message, **kwargs):
       log_data = {
           "message": message,
           **kwargs
       }
       log_str = json.dumps(log_data)
       
       if level == "debug":
           logger.debug(log_str)
       elif level == "info":
           logger.info(log_str)
       # etc.
   
   # Usage
   log_structured("info", "Tool called", tool="web_scrape", url="example.com")
   ```

#### Protocol Tracing

**Approach:**
1. Set up protocol tracing:
   ```python
   # Enable detailed protocol tracing
   os.environ["MCP_TRACE"] = "1"
   ```

2. Log all protocol messages:
   ```python
   async def log_protocol_message(direction, message):
       log_structured(
           "debug",
           f"MCP {direction}",
           message=message,
           timestamp=datetime.now().isoformat()
       )
   
   # Intercept all messages
   original_send = protocol.send
   
   async def logged_send(message):
       await log_protocol_message("SEND", message)
       return await original_send(message)
   
   protocol.send = logged_send
   ```

3. Use MCP Inspector for visual tracing

### Performance Diagnosis

#### Identifying Bottlenecks

**Approach:**
1. Time operations:
   ```python
   import time
   
   @mcp.tool()
   async def slow_operation(param: str) -> str:
       start_time = time.time()
       
       # Operation
       result = await perform_operation(param)
       
       elapsed_time = time.time() - start_time
       logger.info(f"Operation took {elapsed_time:.3f} seconds")
       
       return result
   ```

2. Profile code:
   ```python
   import cProfile
   import pstats
   
   def profile_function(func, *args, **kwargs):
       profiler = cProfile.Profile()
       profiler.enable()
       result = func(*args, **kwargs)
       profiler.disable()
       
       stats = pstats.Stats(profiler).sort_stats("cumtime")
       stats.print_stats(20)  # Print top 20 items
       
       return result
   ```

3. Monitor resource usage:
   ```python
   import psutil
   
   def log_resource_usage():
       process = psutil.Process()
       memory_info = process.memory_info()
       cpu_percent = process.cpu_percent(interval=1)
       
       logger.info(f"Memory usage: {memory_info.rss / 1024 / 1024:.2f} MB")
       logger.info(f"CPU usage: {cpu_percent:.2f}%")
   ```

#### Optimizing Performance

**Approach:**
1. Use connection pooling:
   ```python
   # Create a shared HTTP client
   http_client = httpx.AsyncClient()
   
   @mcp.tool()
   async def fetch_url(url: str) -> str:
       # Use shared client instead of creating a new one each time
       response = await http_client.get(url)
       return response.text
   
   # Clean up on shutdown
   @lifespan.cleanup
   async def close_http_client():
       await http_client.aclose()
   ```

2. Implement caching:
   ```python
   # Simple in-memory cache
   cache = {}
   cache_ttl = {}
   
   async def cached_fetch(url, ttl=300):
       now = time.time()
       
       # Check if in cache and not expired
       if url in cache and now < cache_ttl.get(url, 0):
           return cache[url]
       
       # Fetch and cache
       response = await http_client.get(url)
       result = response.text
       
       cache[url] = result
       cache_ttl[url] = now + ttl
       
       return result
   ```

3. Use async operations effectively:
   ```python
   # Run operations in parallel
   async def fetch_multiple(urls):
       tasks = [http_client.get(url) for url in urls]
       responses = await asyncio.gather(*tasks)
       return [response.text for response in responses]
   ```

### Debugging Complex Servers

#### Interactive Debugging

**Approach:**
1. Set up Python debugger:
   ```python
   import pdb
   
   @mcp.tool()
   def debug_tool(param: str) -> str:
       # Set breakpoint
       pdb.set_trace()
       # Rest of function
   ```

2. Use remote debugging for production:
   ```python
   from debugpy import listen, wait_for_client
   
   # Set up remote debugger
   listen(("0.0.0.0", 5678))
   wait_for_client()  # Wait for the debugger to attach
   ```

3. Use logging-based debugging:
   ```python
   def trace_function(func):
       def wrapper(*args, **kwargs):
           arg_str = ", ".join([
               *[repr(arg) for arg in args],
               *[f"{k}={repr(v)}" for k, v in kwargs.items()]
           ])
           logger.debug(f"CALL: {func.__name__}({arg_str})")
           
           try:
               result = func(*args, **kwargs)
               logger.debug(f"RETURN: {func.__name__} -> {repr(result)}")
               return result
           except Exception as e:
               logger.debug(f"EXCEPTION: {func.__name__} -> {str(e)}")
               raise
       
       return wrapper
   ```

#### Reproducing Issues

**Approach:**
1. Create minimal test cases:
   ```python
   # test_web_scrape.py
   import asyncio
   from server import mcp
   
   async def test_web_scrape():
       # Get tool function
       web_scrape = mcp._tools["web_scrape"]
       
       # Test with different inputs
       result1 = await web_scrape("example.com")
       print(f"Result 1: {result1[:100]}...")
       
       result2 = await web_scrape("invalid^^url")
       print(f"Result 2: {result2}")
       
       # Add more test cases
   
   if __name__ == "__main__":
       asyncio.run(test_web_scrape())
   ```

2. Record and replay protocol sessions:
   ```python
   # Record session
   async def record_session(file_path):
       messages = []
       
       # Intercept messages
       original_send = protocol.send
       original_receive = protocol.receive
       
       async def logged_send(message):
           messages.append({"direction": "send", "message": message})
           return await original_send(message)
       
       async def logged_receive():
           message = await original_receive()
           messages.append({"direction": "receive", "message": message})
           return message
       
       protocol.send = logged_send
       protocol.receive = logged_receive
       
       # Run session
       # ...
       
       # Save recorded session
       with open(file_path, "w") as f:
           json.dump(messages, f, indent=2)
   ```

3. Use request/response mocking:
   ```python
   # Mock HTTP responses
   class MockResponse:
       def __init__(self, text, status_code=200):
           self.text = text
           self.status_code = status_code
       
       def raise_for_status(self):
           if self.status_code >= 400:
               raise httpx.HTTPStatusError(f"HTTP Error: {self.status_code}", request=None, response=self)
   
   # Replace httpx client get method
   async def mock_get(url, **kwargs):
       if url == "https://example.com":
           return MockResponse("<html><body>Example content</body></html>")
       elif url == "https://error.example.com":
           return MockResponse("Error", status_code=500)
       else:
           raise httpx.RequestError(f"Connection error: {url}")
   
   # Apply mock
   httpx.AsyncClient.get = mock_get
   ```

## Conclusion

Troubleshooting MCP servers requires a systematic approach and understanding of the various components involved. By following the guidelines in this document, you should be able to diagnose and resolve most common issues.

Remember these key principles:

1. **Start simple**: Check the basics first (environment, commands, paths)
2. **Use logging**: Enable detailed logging to understand what's happening
3. **Test incrementally**: Test individual components before full integration
4. **Check documentation**: Consult MCP documentation for specifications
5. **Use tools**: Leverage MCP Inspector and other debugging tools

The next document will explain how to extend this repository with new tools.
