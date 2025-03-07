# Extending the Repository with New Tools

This guide explains how to add new tools to the MCP repository. You'll learn best practices for tool design, implementation strategies, and integration techniques that maintain the repository's modular structure.

## Understanding the Repository Structure

Before adding new tools, it's important to understand the existing structure:

```
/MCP/
├── LICENSE
├── README.md
├── requirements.txt
├── server.py
├── streamlit_app.py
├── run.sh
├── run.bat
├── tools/
│   ├── __init__.py
│   └── web_scrape.py
└── docs/
    └── *.md
```

Key components:

1. **server.py**: The main MCP server that registers and exposes tools
2. **tools/**: Directory containing individual tool implementations
3. **streamlit_app.py**: UI for interacting with MCP servers
4. **requirements.txt**: Python dependencies
5. **run.sh/run.bat**: Convenience scripts for running the server or UI

## Planning Your New Tool

Before implementation, plan your tool carefully:

### 1. Define the Purpose

Clearly define what your tool will do:

- What problem does it solve?
- How does it extend the capabilities of an LLM?
- Does it retrieve information, process data, or perform actions?

### 2. Choose a Tool Type

MCP supports different types of tools:

- **Information retrieval tools**: Fetch information from external sources
- **Processing tools**: Transform or analyze data
- **Action tools**: Perform operations with side effects
- **Integration tools**: Connect to external services or APIs

### 3. Design the Interface

Consider the tool's interface:

- What parameters does it need?
- What will it return?
- How will it handle errors?
- What schema will describe it?

Example interface design:

```
Tool: search_news
Purpose: Search for recent news articles by keyword
Parameters:
  - query (string): Search query
  - days (int, optional): How recent the news should be (default: 7)
  - limit (int, optional): Maximum number of results (default: 5)
Returns:
  - List of articles with titles, sources, and summaries
Errors:
  - Handle API timeouts
  - Handle rate limiting
  - Handle empty results
```

## Implementing Your Tool

Now that you've planned your tool, it's time to implement it.

### 1. Create a New Tool Module

Create a new Python file in the `tools` directory:

```bash
touch tools/my_new_tool.py
```

### 2. Implement the Tool Function

Write the core functionality in your new tool file:

```python
# tools/my_new_tool.py
"""
MCP tool for [description of your tool].
"""

import httpx
import asyncio
import json
from typing import List, Dict, Any, Optional


async def search_news(query: str, days: int = 7, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Search for recent news articles based on a query.
    
    Args:
        query: Search terms
        days: How recent the news should be (in days)
        limit: Maximum number of results to return
        
    Returns:
        List of news articles with title, source, and summary
    """
    # Implementation details
    try:
        # API call
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://newsapi.example.com/v2/everything",
                params={
                    "q": query,
                    "from": f"-{days}d",
                    "pageSize": limit,
                    "apiKey": "YOUR_API_KEY"  # In production, use environment variables
                }
            )
            response.raise_for_status()
            data = response.json()
            
            # Process and return results
            articles = data.get("articles", [])
            results = []
            
            for article in articles[:limit]:
                results.append({
                    "title": article.get("title", "No title"),
                    "source": article.get("source", {}).get("name", "Unknown source"),
                    "url": article.get("url", ""),
                    "summary": article.get("description", "No description")
                })
                
            return results
            
    except httpx.HTTPStatusError as e:
        # Handle API errors
        return [{"error": f"API error: {e.response.status_code}"}]
    except httpx.RequestError as e:
        # Handle connection errors
        return [{"error": f"Connection error: {str(e)}"}]
    except Exception as e:
        # Handle unexpected errors
        return [{"error": f"Unexpected error: {str(e)}"}]


# For testing outside of MCP
if __name__ == "__main__":
    async def test():
        results = await search_news("python programming")
        print(json.dumps(results, indent=2))
    
    asyncio.run(test())
```

### 3. Add Required Dependencies

If your tool needs additional dependencies, add them to the requirements.txt file:

```bash
# Add to requirements.txt
httpx>=0.24.0
dateutil>=2.8.2
```

### 4. Register the Tool in the Server

Update the main server.py file to import and register your new tool:

```python
# server.py
from mcp.server.fastmcp import FastMCP

# Import existing tools
from tools.web_scrape import fetch_url_as_markdown

# Import your new tool
from tools.my_new_tool import search_news

# Create an MCP server
mcp = FastMCP("Web Tools")

# Register existing tools
@mcp.tool()
async def web_scrape(url: str) -> str:
    """
    Convert a URL to use r.jina.ai as a prefix and fetch the markdown content.
    
    Args:
        url (str): The URL to convert and fetch.
        
    Returns:
        str: The markdown content if successful, or an error message if not.
    """
    return await fetch_url_as_markdown(url)

# Register your new tool
@mcp.tool()
async def news_search(query: str, days: int = 7, limit: int = 5) -> str:
    """
    Search for recent news articles based on a query.
    
    Args:
        query: Search terms
        days: How recent the news should be (in days, default: 7)
        limit: Maximum number of results to return (default: 5)
        
    Returns:
        Formatted text with news article information
    """
    articles = await search_news(query, days, limit)
    
    # Format the results as text
    if articles and "error" in articles[0]:
        return articles[0]["error"]
    
    if not articles:
        return "No news articles found for the given query."
    
    results = []
    for i, article in enumerate(articles, 1):
        results.append(f"## {i}. {article['title']}")
        results.append(f"Source: {article['source']}")
        results.append(f"URL: {article['url']}")
        results.append(f"\n{article['summary']}\n")
    
    return "\n".join(results)

if __name__ == "__main__":
    mcp.run()
```

## Best Practices for Tool Implementation

### Error Handling

Robust error handling is essential for reliable tools:

```python
try:
    # Operation that might fail
    result = await perform_operation()
    return result
except SpecificError as e:
    # Handle specific error cases
    return f"Operation failed: {str(e)}"
except Exception as e:
    # Catch-all for unexpected errors
    logging.error(f"Unexpected error: {str(e)}")
    return "An unexpected error occurred. Please try again later."
```

### Input Validation

Validate inputs before processing:

```python
def validate_search_params(query: str, days: int, limit: int) -> Optional[str]:
    """Validate search parameters and return error message if invalid."""
    if not query or len(query.strip()) == 0:
        return "Search query cannot be empty"
    
    if days < 1 or days > 30:
        return "Days must be between 1 and 30"
    
    if limit < 1 or limit > 100:
        return "Limit must be between 1 and 100"
    
    return None

# In the tool function
error = validate_search_params(query, days, limit)
if error:
    return error
```

### Security Considerations

Implement security best practices:

```python
# Sanitize inputs
def sanitize_query(query: str) -> str:
    """Remove potentially dangerous characters from query."""
    import re
    return re.sub(r'[^\w\s\-.,?!]', '', query)

# Use environment variables for secrets
import os
api_key = os.environ.get("NEWS_API_KEY")
if not api_key:
    return "API key not configured. Please set the NEWS_API_KEY environment variable."

# Implement rate limiting
from functools import lru_cache
import time

@lru_cache(maxsize=100)
def get_last_call_time():
    return time.time()

def respect_rate_limit(min_interval=1.0):
    """Ensure minimum time between API calls."""
    last_call = get_last_call_time()
    now = time.time()
    if now - last_call < min_interval:
        time.sleep(min_interval - (now - last_call))
    get_last_call_time.cache_clear()
    get_last_call_time()
```

### Docstrings and Comments

Write clear documentation:

```python
async def translate_text(text: str, target_language: str) -> str:
    """
    Translate text to another language.
    
    This tool uses an external API to translate text from one language to another.
    It automatically detects the source language and translates to the specified
    target language.
    
    Args:
        text: The text to translate
        target_language: ISO 639-1 language code (e.g., 'es' for Spanish)
        
    Returns:
        Translated text in the target language
        
    Raises:
        ValueError: If the target language is not supported
    """
    # Implementation
```

### Testing

Include tests for your tools:

```python
# tools/tests/test_my_new_tool.py
import pytest
import asyncio
from tools.my_new_tool import search_news

@pytest.mark.asyncio
async def test_search_news_valid_query():
    """Test search_news with a valid query."""
    results = await search_news("test query")
    assert isinstance(results, list)
    assert len(results) > 0

@pytest.mark.asyncio
async def test_search_news_empty_query():
    """Test search_news with an empty query."""
    results = await search_news("")
    assert isinstance(results, list)
    assert "error" in results[0]

# Run tests
if __name__ == "__main__":
    asyncio.run(pytest.main(["-xvs", "test_my_new_tool.py"]))
```

## Managing Tool Configurations

For tools that require configuration, follow these practices:

### Environment Variables

Use environment variables for configuration:

```python
# tools/my_new_tool.py
import os

API_KEY = os.environ.get("MY_TOOL_API_KEY")
BASE_URL = os.environ.get("MY_TOOL_BASE_URL", "https://api.default.com")
```

### Configuration Files

For more complex configurations, use configuration files:

```python
# tools/config.py
import json
import os
from pathlib import Path

def load_config(tool_name):
    """Load tool-specific configuration."""
    config_dir = Path(os.environ.get("MCP_CONFIG_DIR", "~/.mcp")).expanduser()
    config_path = config_dir / f"{tool_name}.json"
    
    if not config_path.exists():
        return {}
    
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {str(e)}")
        return {}

# In your tool file
from tools.config import load_config

config = load_config("my_new_tool")
api_key = config.get("api_key", os.environ.get("MY_TOOL_API_KEY", ""))
```

## Advanced Tool Patterns

### Composition

Compose multiple tools for complex functionality:

```python
async def search_and_summarize(query: str) -> str:
    """Search for news and summarize the results."""
    # First search for news
    articles = await search_news(query, days=3, limit=3)
    
    if not articles or "error" in articles[0]:
        return "Failed to find news articles."
    
    # Then summarize each article
    summaries = []
    for article in articles:
        summary = await summarize_text(article["summary"])
        summaries.append(f"Title: {article['title']}\nSummary: {summary}")
    
    return "\n\n".join(summaries)
```

### Stateful Tools

For tools that need to maintain state:

```python
# tools/stateful_tool.py
from typing import Dict, Any
import json
import os
from pathlib import Path

class SessionStore:
    """Simple file-based session store."""
    
    def __init__(self, tool_name):
        self.storage_dir = Path(os.environ.get("MCP_STORAGE_DIR", "~/.mcp/storage")).expanduser()
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.tool_name = tool_name
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self._load()
    
    def _get_storage_path(self):
        return self.storage_dir / f"{self.tool_name}_sessions.json"
    
    def _load(self):
        path = self._get_storage_path()
        if path.exists():
            try:
                with open(path, "r") as f:
                    self.sessions = json.load(f)
            except Exception:
                self.sessions = {}
    
    def _save(self):
        with open(self._get_storage_path(), "w") as f:
            json.dump(self.sessions, f, indent=2)
    
    def get(self, session_id, key, default=None):
        session = self.sessions.get(session_id, {})
        return session.get(key, default)
    
    def set(self, session_id, key, value):
        if session_id not in self.sessions:
            self.sessions[session_id] = {}
        self.sessions[session_id][key] = value
        self._save()
    
    def clear(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]
            self._save()

# Usage in a tool
from tools.stateful_tool import SessionStore

# Initialize store
session_store = SessionStore("conversation")

async def remember_fact(session_id: str, fact: str) -> str:
    """Remember a fact for later recall."""
    facts = session_store.get(session_id, "facts", [])
    facts.append(fact)
    session_store.set(session_id, "facts", facts)
    return f"I'll remember that: {fact}"

async def recall_facts(session_id: str) -> str:
    """Recall previously stored facts."""
    facts = session_store.get(session_id, "facts", [])
    if not facts:
        return "I don't have any facts stored for this session."
    
    return "Here are the facts I remember:\n- " + "\n- ".join(facts)
```

### Long-Running Operations

For tools that take time to complete:

```python
from mcp.server.fastmcp import FastMCP, Context

@mcp.tool()
async def process_large_dataset(dataset_url: str, ctx: Context) -> str:
    """Process a large dataset with progress reporting."""
    try:
        # Download dataset
        ctx.info(f"Downloading dataset from {dataset_url}")
        await ctx.report_progress(10)
        
        # Process in chunks
        total_chunks = 10
        for i in range(total_chunks):
            ctx.info(f"Processing chunk {i+1}/{total_chunks}")
            # Process chunk
            await asyncio.sleep(1)  # Simulate work
            await ctx.report_progress(10 + (i+1) * 80 // total_chunks)
        
        # Finalize
        ctx.info("Finalizing results")
        await ctx.report_progress(90)
        await asyncio.sleep(1)  # Simulate work
        
        # Complete
        await ctx.report_progress(100)
        return "Dataset processing complete. Found 42 insights."
        
    except Exception as e:
        ctx.info(f"Error: {str(e)}")
        return f"Processing failed: {str(e)}"
```

## Adding a Resource

In addition to tools, you might want to add a resource to your MCP server:

```python
# server.py
@mcp.resource("weather://{location}")
async def get_weather(location: str) -> str:
    """
    Get weather information for a location.
    
    Args:
        location: City name or coordinates
    
    Returns:
        Weather information as text
    """
    try:
        # Fetch weather data
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.weatherapi.com/v1/current.json",
                params={
                    "q": location,
                    "key": os.environ.get("WEATHER_API_KEY", "")
                }
            )
            response.raise_for_status()
            data = response.json()
        
        # Format weather data
        location_data = data.get("location", {})
        current_data = data.get("current", {})
        
        weather_info = f"""
        Weather for {location_data.get('name', location)}, {location_data.get('country', '')}
        
        Temperature: {current_data.get('temp_c', 'N/A')}°C / {current_data.get('temp_f', 'N/A')}°F
        Condition: {current_data.get('condition', {}).get('text', 'N/A')}
        Wind: {current_data.get('wind_kph', 'N/A')} kph, {current_data.get('wind_dir', 'N/A')}
        Humidity: {current_data.get('humidity', 'N/A')}%
        Updated: {current_data.get('last_updated', 'N/A')}
        """
        
        return weather_info
        
    except Exception as e:
        return f"Error fetching weather: {str(e)}"
```

## Adding a Prompt

You can also add a prompt to your MCP server:

```python
# server.py
@mcp.prompt()
def analyze_sentiment(text: str) -> str:
    """
    Create a prompt for sentiment analysis.
    
    Args:
        text: The text to analyze
    
    Returns:
        A prompt for sentiment analysis
    """
    return f"""
    Please analyze the sentiment of the following text and categorize it as positive, negative, or neutral. 
    Provide a brief explanation for your categorization and highlight key phrases that indicate the sentiment.
    
    Text to analyze:
    
    {text}
    
    Your analysis:
    """
```

## Conclusion

Extending the MCP repository with new tools is a powerful way to enhance the capabilities of LLMs. By following the patterns and practices outlined in this guide, you can create robust, reusable tools that integrate seamlessly with the existing repository structure.

Remember these key principles:

1. **Plan before coding**: Define the purpose and interface of your tool
2. **Follow best practices**: Implement proper error handling, input validation, and security
3. **Document thoroughly**: Write clear docstrings and comments
4. **Test rigorously**: Create tests for your tools
5. **Consider configurations**: Use environment variables or configuration files
6. **Explore advanced patterns**: Implement composition, state, and long-running operations as needed

In the next document, we'll explore example use cases for your MCP server and tools.
