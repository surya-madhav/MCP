# Advanced MCP Features

This document explores advanced features and configurations for Model Context Protocol (MCP) servers. These techniques can help you build more powerful, secure, and maintainable MCP implementations.

## Advanced Configuration

### Server Lifecycle Management

The MCP server lifecycle can be managed with the `lifespan` parameter to set up resources on startup and clean them up on shutdown:

```python
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any
from mcp.server.fastmcp import FastMCP

@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """Manage server lifecycle."""
    print("Server starting up...")
    
    # Initialize resources
    db_connection = await initialize_database()
    cache = initialize_cache()
    
    try:
        # Yield context to server
        yield {
            "db": db_connection,
            "cache": cache
        }
    finally:
        # Clean up resources
        print("Server shutting down...")
        await db_connection.close()
        cache.clear()

# Create server with lifespan
mcp = FastMCP("AdvancedServer", lifespan=server_lifespan)

# Access lifespan context in tools
@mcp.tool()
async def query_database(sql: str, ctx: Context) -> str:
    """Run a database query."""
    db = ctx.request_context.lifespan_context["db"]
    results = await db.execute(sql)
    return results
```

### Dependency Specification

You can specify dependencies for your server to ensure it has everything it needs:

```python
# Specify dependencies for the server
mcp = FastMCP(
    "DependentServer",
    dependencies=[
        "pandas>=1.5.0",
        "numpy>=1.23.0",
        "scikit-learn>=1.1.0"
    ]
)
```

This helps with:
- Documentation for users
- Verification during installation
- Clarity about requirements

### Environment Variables

Use environment variables for configuration:

```python
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access environment variables
API_KEY = os.environ.get("MY_API_KEY")
BASE_URL = os.environ.get("MY_BASE_URL", "https://api.default.com")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

# Create server with configuration
mcp = FastMCP(
    "ConfigurableServer",
    config={
        "api_key": API_KEY,
        "base_url": BASE_URL,
        "debug": DEBUG
    }
)

# Access configuration in tools
@mcp.tool()
async def call_api(endpoint: str, ctx: Context) -> str:
    """Call an API endpoint."""
    config = ctx.server.config
    base_url = config["base_url"]
    api_key = config["api_key"]
    
    # Use configuration
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{base_url}/{endpoint}",
            headers={"Authorization": f"Bearer {api_key}"}
        )
        return response.text
```

## Advanced Logging

### Structured Logging

Implement structured logging for better analysis:

```python
import logging
import json
from datetime import datetime

class StructuredFormatter(logging.Formatter):
    """Format logs as JSON for structured logging."""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add custom fields if present
        if hasattr(record, "data"):
            log_data.update(record.data)
        
        return json.dumps(log_data)

# Set up structured logging
logger = logging.getLogger("mcp")
handler = logging.FileHandler("mcp_server.log")
handler.setFormatter(StructuredFormatter())
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# Log with extra data
def log_with_data(level, message, **kwargs):
    record = logging.LogRecord(
        name="mcp",
        level=level,
        pathname="",
        lineno=0,
        msg=message,
        args=(),
        exc_info=None
    )
    record.data = kwargs
    logger.handle(record)

# Usage
log_with_data(
    logging.INFO,
    "Tool execution completed",
    tool="web_scrape",
    url="example.com",
    execution_time=1.25,
    result_size=1024
)
```

### Client Notifications

Send logging messages to clients:

```python
@mcp.tool()
async def process_data(data: str, ctx: Context) -> str:
    """Process data with client notifications."""
    try:
        # Send info message to client
        ctx.info("Starting data processing")
        
        # Process data in steps
        ctx.info("Step 1: Parsing data")
        parsed_data = parse_data(data)
        
        ctx.info("Step 2: Analyzing data")
        analysis = analyze_data(parsed_data)
        
        ctx.info("Step 3: Generating report")
        report = generate_report(analysis)
        
        ctx.info("Processing complete")
        return report
        
    except Exception as e:
        # Send error message to client
        ctx.error(f"Processing failed: {str(e)}")
        raise
```

### Progress Reporting

Report progress for long-running operations:

```python
@mcp.tool()
async def process_large_file(file_path: str, ctx: Context) -> str:
    """Process a large file with progress reporting."""
    try:
        # Get file size
        file_size = os.path.getsize(file_path)
        bytes_processed = 0
        
        # Open file
        async with aiofiles.open(file_path, "rb") as f:
            # Process in chunks
            chunk_size = 1024 * 1024  # 1 MB
            while True:
                chunk = await f.read(chunk_size)
                if not chunk:
                    break
                    
                # Process chunk
                process_chunk(chunk)
                
                # Update progress
                bytes_processed += len(chunk)
                progress = min(100, int(bytes_processed * 100 / file_size))
                await ctx.report_progress(progress)
                
                # Log milestone
                if progress % 10 == 0:
                    ctx.info(f"Processed {progress}% of file")
        
        return f"File processing complete. Processed {file_size} bytes."
        
    except Exception as e:
        ctx.error(f"File processing failed: {str(e)}")
        return f"Error: {str(e)}"
```

## Security Features

### Input Validation

Implement thorough input validation:

```python
from pydantic import BaseModel, Field, validator

class SearchParams(BaseModel):
    """Validated search parameters."""
    query: str = Field(..., min_length=1, max_length=100)
    days: int = Field(7, ge=1, le=30)
    limit: int = Field(5, ge=1, le=100)
    
    @validator('query')
    def query_must_be_valid(cls, v):
        import re
        if not re.match(r'^[a-zA-Z0-9\s\-.,?!]+$', v):
            raise ValueError('Query contains invalid characters')
        return v

@mcp.tool()
async def search_with_validation(params: dict) -> str:
    """Search with validated parameters."""
    try:
        # Validate parameters
        validated = SearchParams(**params)
        
        # Proceed with validated parameters
        results = await perform_search(
            validated.query,
            validated.days,
            validated.limit
        )
        
        return format_results(results)
        
    except Exception as e:
        return f"Validation error: {str(e)}"
```

### Rate Limiting

Implement rate limiting to prevent abuse:

```python
import time
from functools import wraps

# Simple rate limiter
class RateLimiter:
    def __init__(self, calls_per_minute=60):
        self.calls_per_minute = calls_per_minute
        self.interval = 60 / calls_per_minute  # seconds per call
        self.last_call_times = {}
    
    async def limit(self, key):
        """Limit calls for a specific key."""
        now = time.time()
        
        # Initialize if first call
        if key not in self.last_call_times:
            self.last_call_times[key] = [now]
            return
        
        # Get calls within the last minute
        minute_ago = now - 60
        recent_calls = [t for t in self.last_call_times[key] if t > minute_ago]
        
        # Check if rate limit exceeded
        if len(recent_calls) >= self.calls_per_minute:
            oldest_call = min(recent_calls)
            wait_time = 60 - (now - oldest_call)
            raise ValueError(f"Rate limit exceeded. Try again in {wait_time:.1f} seconds.")
        
        # Update call times
        self.last_call_times[key] = recent_calls + [now]

# Create rate limiter
rate_limiter = RateLimiter(calls_per_minute=10)

# Apply rate limiting to a tool
@mcp.tool()
async def rate_limited_api_call(endpoint: str) -> str:
    """Call API with rate limiting."""
    try:
        # Apply rate limit
        await rate_limiter.limit("api_call")
        
        # Proceed with API call
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.example.com/{endpoint}")
            return response.text
            
    except ValueError as e:
        return f"Error: {str(e)}"
```

### Access Control

Implement access controls for sensitive operations:

```python
# Define access levels
class AccessLevel:
    READ = 1
    WRITE = 2
    ADMIN = 3

# Access control decorator
def require_access(level):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get context from args
            ctx = None
            for arg in args:
                if isinstance(arg, Context):
                    ctx = arg
                    break
            
            if ctx is None:
                for arg_name, arg_value in kwargs.items():
                    if isinstance(arg_value, Context):
                        ctx = arg_value
                        break
            
            if ctx is None:
                return "Error: Context not provided"
            
            # Check access level
            user_level = get_user_access_level(ctx)
            if user_level < level:
                return "Error: Insufficient permissions"
            
            # Proceed with function
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Get user access level from context
def get_user_access_level(ctx):
    # In practice, this would use authentication information
    # For demonstration, return READ
