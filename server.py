#!/usr/bin/env python3
import sys

"""
MCP Server with web scraping tool.

This server implements a Model Context Protocol (MCP) server that provides web scraping
functionality. It offers a tool to convert regular URLs into r.jina.ai prefixed URLs
and fetch their content as markdown. This allows for easy conversion of web content
into a markdown format suitable for various applications.

Key Features:
- URL conversion and fetching
- Support for both stdio and SSE transport mechanisms
- Command-line configuration options
- Asynchronous web scraping functionality
"""

import argparse
from mcp.server.fastmcp import FastMCP

# Import our custom tools
from tools.web_scrape import fetch_url_as_markdown
from tools.ddg_search import search_duckduckgo
from tools.crawl4ai_scraper import crawl_and_extract_markdown

# Initialize the MCP server with a descriptive name that reflects its purpose
mcp = FastMCP("Web Tools")

@mcp.tool()
async def web_scrape(url: str) -> str:
    """
    Convert a URL to use r.jina.ai as a prefix and fetch the markdown content.
    This tool wraps the fetch_url_as_markdown function to expose it as an MCP tool.
    
    Args:
        url (str): The URL to convert and fetch. Can be with or without http(s):// prefix.
        
    Returns:
        str: The markdown content if successful, or an error message if not.
    """
    return await fetch_url_as_markdown(url)

@mcp.tool()
async def ddg_search(query: str, region: str = "wt-wt", safesearch: str = "moderate", timelimit: str = None, max_results: int = 10) -> str:
    """
    Search the web using DuckDuckGo and return formatted results.
    
    Args:
        query (str): The search query to look for.
        region (str, optional): Region code for search results, e.g., "wt-wt" (worldwide), "us-en" (US English). Defaults to "wt-wt".
        safesearch (str, optional): SafeSearch level: "on", "moderate", or "off". Defaults to "moderate".
        timelimit (str, optional): Time limit for results: "d" (day), "w" (week), "m" (month), "y" (year). Defaults to None.
        max_results (int, optional): Maximum number of results to return. Defaults to 10.
        
    Returns:
        str: Formatted search results as text, or an error message if the search fails.
    """
    return await search_duckduckgo(keywords=query, region=region, safesearch=safesearch, timelimit=timelimit, max_results=max_results)

@mcp.tool()
async def advanced_scrape(url: str) -> str:
    """
    Scrape a webpage using advanced techniques and return clean, well-formatted markdown.
    
    This tool uses Crawl4AI to extract the main content from a webpage while removing
    navigation bars, sidebars, footers, ads, and other non-essential elements. The result
    is clean, well-formatted markdown focused on the actual content of the page.
    
    Args:
        url (str): The URL to scrape. Can be with or without http(s):// prefix.
        
    Returns:
        str: Well-formatted markdown content if successful, or an error message if not.
    """
    return await crawl_and_extract_markdown(url)

if __name__ == "__main__":
    # Log Python version for debugging purposes
    print(f"Using Python {sys.version}", file=sys.stderr)
    
    # Set up command-line argument parsing with descriptive help messages
    parser = argparse.ArgumentParser(description="MCP Server with web tools")
    parser.add_argument(
        "--transport", 
        choices=["stdio", "sse"], 
        default="stdio",
        help="Transport mechanism to use (default: stdio)"
    )
    parser.add_argument(
        "--host", 
        default="localhost",
        help="Host to bind to when using SSE transport (default: localhost)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=5000,
        help="Port to bind to when using SSE transport (default: 5000)"
    )    
    args = parser.parse_args()
    
    # Start the server with the specified transport mechanism
    if args.transport == "stdio":
        print("Starting MCP server with stdio transport...", file=sys.stderr)
        mcp.run(transport="stdio")
    else:
        print(f"Starting MCP server with SSE transport on {args.host}:{args.port}...", file=sys.stderr)
        mcp.run(transport="sse", host=args.host, port=args.port)
