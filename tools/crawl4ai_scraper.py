"""
Crawl4AI web scraping tool for MCP server.

This module provides advanced web scraping functionality using Crawl4AI.
It extracts content from web pages, removes non-essential elements like
navigation bars, footers, and sidebars, and returns well-formatted markdown
that preserves document structure including headings, code blocks, tables,
and image references.

Features:
- Clean content extraction with navigation, sidebar, and footer removal
- Preserves document structure (headings, lists, tables, code blocks)
- Automatic conversion to well-formatted markdown
- Support for JavaScript-rendered content
- Content filtering to focus on the main article/content
- Comprehensive error handling
"""

import asyncio
import os
import re
import logging
from typing import Optional

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("crawl4ai_scraper")

async def crawl_and_extract_markdown(url: str, query: Optional[str] = None) -> str:
    """
    Crawl a webpage and extract well-formatted markdown content.
    
    Args:
        url: The URL to crawl
        query: Optional search query to focus content on (if None, extracts main content)
    
    Returns:
        str: Well-formatted markdown content from the webpage
    
    Raises:
        Exception: If crawling fails or content extraction encounters errors
    """
    try:
        # Configure the browser for optimal rendering
        browser_config = BrowserConfig(
            headless=True,
            viewport_width=1920,  # Wider viewport to capture more content
            viewport_height=1080,  # Taller viewport for the same reason
            java_script_enabled=True,
            text_mode=False,  # Set to False to ensure all content is loaded
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Create a content filter for removing unwanted elements
        content_filter = PruningContentFilter(
            threshold=0.1,  # Very low threshold to keep more content
            threshold_type="dynamic",  # Dynamic threshold based on page content
            min_word_threshold=2  # Include very short text blocks for headings/code
        )
        
        # Configure markdown generator with options for structure preservation
        markdown_generator = DefaultMarkdownGenerator(
            content_filter=content_filter,
            options={
                "body_width": 0,         # No wrapping
                "ignore_images": False,   # Keep image references
                "citations": True,        # Include link citations
                "escape_html": False,     # Don't escape HTML in code blocks
                "include_sup_sub": True,  # Preserve superscript/subscript
                "pad_tables": True,       # Better table formatting
                "mark_code": True,        # Better code block preservation
                "code_language": "",      # Default code language
                "wrap_links": False       # Preserve link formatting
            }
        )
        
        # Configure the crawler run for optimal structure extraction
        run_config = CrawlerRunConfig(
            verbose=False,
            # Content filtering
            markdown_generator=markdown_generator,
            word_count_threshold=2,  # Extremely low to include very short text blocks
            
            # Tag exclusions - remove unwanted elements
            excluded_tags=["nav", "footer", "aside"],
            excluded_selector=".nav, .navbar, .sidebar, .footer, #footer, #sidebar, " +
                             ".ads, .advertisement, .navigation, #navigation, " +
                             ".menu, #menu, .toc, .table-of-contents",
            
            # Wait conditions for JS content
            wait_until="networkidle",
            wait_for="css:pre, code, h1, h2, h3, table",  # Wait for important structural elements 
            page_timeout=60000,
            
            # Don't limit to specific selectors to get full content
            css_selector=None,
            
            # Other options
            remove_overlay_elements=True,    # Remove modal popups
            remove_forms=True,               # Remove forms
            scan_full_page=True,             # Scan the full page
            scroll_delay=0.5,                # Slower scroll for better content loading
            cache_mode=CacheMode.BYPASS      # Bypass cache for fresh content
        )
        
        # Create crawler and run it
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=url, config=run_config)
            
            if not result.success:
                raise Exception(f"Crawl failed: {result.error_message}")
            
            # Extract the title from metadata if available
            title = "Untitled Document"
            if result.metadata and "title" in result.metadata:
                title = result.metadata["title"]
            
            # Choose the best markdown content
            markdown_content = ""
            
            # Try to get the best version of the markdown
            if hasattr(result, "markdown_v2") and result.markdown_v2:
                if hasattr(result.markdown_v2, 'raw_markdown') and result.markdown_v2.raw_markdown:
                    markdown_content = result.markdown_v2.raw_markdown
                elif hasattr(result.markdown_v2, 'markdown_with_citations') and result.markdown_v2.markdown_with_citations:
                    markdown_content = result.markdown_v2.markdown_with_citations
            elif hasattr(result, "markdown") and result.markdown:
                if isinstance(result.markdown, str):
                    markdown_content = result.markdown
                elif hasattr(result.markdown, 'raw_markdown'):
                    markdown_content = result.markdown.raw_markdown
            elif result.cleaned_html:
                from html2text import html2text
                markdown_content = html2text(result.cleaned_html)
            
            # Post-process the markdown to fix common issues
            
            # 1. Fix code blocks - ensure they have proper formatting
            markdown_content = re.sub(r'```\s*\n', '```python\n', markdown_content)
            
            # 2. Fix broken headings - ensure space after # characters
            markdown_content = re.sub(r'^(#{1,6})([^#\s])', r'\1 \2', markdown_content, flags=re.MULTILINE)
            
            # 3. Add spacing between sections for readability
            markdown_content = re.sub(r'(\n#{1,6} .+?\n)(?=[^\n])', r'\1\n', markdown_content)
            
            # 4. Fix bullet points - ensure proper spacing
            markdown_content = re.sub(r'^\*([^\s])', r'* \1', markdown_content, flags=re.MULTILINE)
            
            # 5. Format the final content with title and URL
            final_content = f"Title: {title}\n\nURL Source: {result.url}\n\nMarkdown Content:\n{markdown_content}"
            
            return final_content
                
    except Exception as e:
        logger.error(f"Error crawling {url}: {str(e)}")
        raise Exception(f"Error crawling {url}: {str(e)}")

# Standalone test functionality
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract structured markdown content from a webpage")
    parser.add_argument("url", nargs="?", default="https://docs.llamaindex.ai/en/stable/understanding/agent/", 
                        help="URL to crawl (default: https://docs.llamaindex.ai/en/stable/understanding/agent/)")
    parser.add_argument("--output", help="Output file to save the markdown (default: scraped_content.md)")
    parser.add_argument("--query", help="Optional search query to focus content")
    
    args = parser.parse_args()
    
    async def test():
        url = args.url
        print(f"Scraping {url}...")
        
        try:
            if args.query:
                result = await crawl_and_extract_markdown(url, args.query)
            else:
                result = await crawl_and_extract_markdown(url)
            
            # Show preview of content
            preview_length = min(1000, len(result))
            print("\nResult Preview (first 1000 chars):")
            print(result[:preview_length] + "...\n" if len(result) > preview_length else result)
            
            # Print statistics
            print(f"\nMarkdown length: {len(result)} characters")
            
            # Save to file
            output_file = args.output if args.output else "scraped_content.md"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"Full content saved to '{output_file}'")
            
            return 0
        except Exception as e:
            print(f"Error: {str(e)}")
            return 1
    
    # Run the test function in an async event loop
    exit_code = asyncio.run(test())
    import sys
    sys.exit(exit_code)
