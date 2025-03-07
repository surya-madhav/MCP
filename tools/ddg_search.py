"""
DuckDuckGo search tool for MCP server.

This module provides functionality to search the web using DuckDuckGo's search engine.
It leverages the duckduckgo_search package to perform text-based web searches and
returns formatted results.

Features:
- Web search with customizable parameters
- Region-specific search support
- SafeSearch filtering options
- Time-limited search results
- Maximum results configuration
- Error handling for rate limits and timeouts
"""

from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import (
    DuckDuckGoSearchException,
    RatelimitException,
    TimeoutException
)

async def search_duckduckgo(
    keywords: str,
    region: str = "wt-wt",
    safesearch: str = "moderate",
    timelimit: str = None,
    max_results: int = 10
) -> str:
    """
    Perform a web search using DuckDuckGo and return formatted results.
    
    Args:
        keywords (str): The search query/keywords to search for.
        region (str, optional): Region code for search results. Defaults to "wt-wt" (worldwide).
        safesearch (str, optional): SafeSearch level: "on", "moderate", or "off". Defaults to "moderate".
        timelimit (str, optional): Time limit for results: "d" (day), "w" (week), "m" (month), "y" (year).
            Defaults to None (no time limit).
        max_results (int, optional): Maximum number of results to return. Defaults to 10.
    
    Returns:
        str: Formatted search results as text, or an error message if the search fails.
    """
    try:
        # Create a DuckDuckGo search instance
        ddgs = DDGS()
        
        # Perform the search with the given parameters
        results = ddgs.text(
            keywords=keywords,
            region=region,
            safesearch=safesearch,
            timelimit=timelimit,
            max_results=max_results
        )
        
        # Format the results into a readable string
        formatted_results = []
        
        # Check if results is empty
        if not results:
            return "No results found for your search query."
        
        # Process and format each result
        for i, result in enumerate(results, 1):
            formatted_result = (
                f"{i}. {result.get('title', 'No title')}\n"
                f"   URL: {result.get('href', 'No URL')}\n"
                f"   {result.get('body', 'No description')}\n"
            )
            formatted_results.append(formatted_result)
        
        # Join all formatted results with a separator
        return "\n".join(formatted_results)
    
    except RatelimitException:
        return "Error: DuckDuckGo search rate limit exceeded. Please try again later."
    
    except TimeoutException:
        return "Error: The search request timed out. Please try again."
    
    except DuckDuckGoSearchException as e:
        return f"Error: DuckDuckGo search failed - {str(e)}"
    
    except Exception as e:
        return f"Error: An unexpected error occurred - {str(e)}"

# Standalone test functionality
if __name__ == "__main__":
    import asyncio
    
    async def test():
        # Example usage with a test query
        query = "Python programming language"
        result = await search_duckduckgo(query, max_results=3)
        print(f"Search results for '{query}':")
        print(result)
    
    # Run the test function in an async event loop
    asyncio.run(test())
