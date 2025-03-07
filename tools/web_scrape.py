"""
Web scraping tool for MCP server.

This module provides functionality to convert regular URLs into r.jina.ai prefixed URLs
and fetch their content as markdown. The r.jina.ai service acts as a URL-to-markdown
converter, making web content more accessible for text processing and analysis.

Features:
- Automatic HTTP/HTTPS scheme addition if missing
- URL conversion to r.jina.ai format
- Asynchronous HTTP requests using httpx
- Comprehensive error handling for various failure scenarios
"""

import httpx

async def fetch_url_as_markdown(url: str) -> str:
    """
    Convert a URL to use r.jina.ai as a prefix and fetch the markdown content.
    
    This function performs the following steps:
    1. Ensures the URL has a proper HTTP/HTTPS scheme
    2. Converts the URL to use r.jina.ai as a prefix
    3. Fetches the content using an async HTTP client
    4. Returns the markdown content or an error message
    
    Args:
        url (str): The URL to convert and fetch. If the URL doesn't start with
                  'http://' or 'https://', 'https://' will be automatically added.
    
    Returns:
        str: The markdown content if successful, or a descriptive error message if:
             - The HTTP request fails (e.g., 404, 500)
             - The connection times out
             - Any other unexpected error occurs
    """
    # Ensure URL has a scheme - default to https:// if none provided
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Convert the URL to use r.jina.ai as a markdown conversion service
    converted_url = f"https://r.jina.ai/{url}"
    
    try:
        # Use httpx for modern async HTTP requests with timeout and redirect handling
        async with httpx.AsyncClient() as client:
            response = await client.get(converted_url, follow_redirects=True, timeout=30.0)
            response.raise_for_status()
            return response.text
    except httpx.HTTPStatusError as e:
        # Handle HTTP errors (4xx, 5xx) with specific status code information
        return f"Error: HTTP status error - {e.response.status_code}"
    except httpx.RequestError as e:
        # Handle network-related errors (timeouts, connection issues, etc.)
        return f"Error: Request failed - {str(e)}"
    except Exception as e:
        # Handle any unexpected errors that weren't caught by the above
        return f"Error: Unexpected error occurred - {str(e)}"

# Standalone test functionality
if __name__ == "__main__":
    import asyncio
    
    async def test():
        # Example usage with a test URL
        url = "example.com"
        result = await fetch_url_as_markdown(url)
        print(f"Fetched content from {url}:")
        # Show preview of content (first 200 characters)
        print(result[:200] + "..." if len(result) > 200 else result)
    
    # Run the test function in an async event loop
    asyncio.run(test())
