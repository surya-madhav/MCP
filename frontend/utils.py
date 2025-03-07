import os
import json
import json5
import streamlit as st
import subprocess
import asyncio
import sys
import shutil
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Define default config path based on OS
default_config_path = os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json")

def load_config(config_path):
    """Load the Claude Desktop config file"""
    try:
        with open(config_path, 'r') as f:
            # Use json5 to handle potential JSON5 format (comments, trailing commas)
            return json5.load(f)
    except Exception as e:
        st.error(f"Error loading config file: {str(e)}")
        return None

def find_executable(name):
    """Find the full path to an executable"""
    path = shutil.which(name)
    if path:
        return path
    
    # Try common locations for Node.js executables
    if name in ['node', 'npm', 'npx']:
        # Check user's home directory for nvm or other Node.js installations
        home = Path.home()
        possible_paths = [
            home / '.nvm' / 'versions' / 'node' / '*' / 'bin' / name,
            home / 'node_modules' / '.bin' / name,
            home / '.npm-global' / 'bin' / name,
            # Add Mac Homebrew path
            Path('/usr/local/bin') / name,
            Path('/opt/homebrew/bin') / name,
        ]
        
        for p in possible_paths:
            if isinstance(p, Path) and '*' in str(p):
                # Handle wildcard paths
                parent = p.parent.parent
                if parent.exists():
                    for version_dir in parent.glob('*'):
                        full_path = version_dir / 'bin' / name
                        if full_path.exists():
                            return str(full_path)
            elif Path(str(p)).exists():
                return str(p)
    
    return None

def check_node_installations():
    """Check if Node.js, npm, and npx are installed and return their versions"""
    node_installed = bool(find_executable('node'))
    node_version = None
    npm_installed = bool(find_executable('npm'))
    npm_version = None
    npx_installed = bool(find_executable('npx'))
    npx_version = None

    if node_installed:
        try:
            node_version = subprocess.check_output([find_executable('node'), '--version']).decode().strip()
        except:
            pass

    if npm_installed:
        try:
            npm_version = subprocess.check_output([find_executable('npm'), '--version']).decode().strip()
        except:
            pass
            
    if npx_installed:
        try:
            npx_version = subprocess.check_output([find_executable('npx'), '--version']).decode().strip()
        except:
            pass
    
    return {
        'node': {'installed': node_installed, 'version': node_version},
        'npm': {'installed': npm_installed, 'version': npm_version},
        'npx': {'installed': npx_installed, 'version': npx_version}
    }

async def connect_to_server(command, args=None, env=None):
    """Connect to an MCP server and list its tools"""
    try:
        # Find the full path to the command
        print(f"Finding executable for command: {command}")
        full_command = find_executable(command)
        if not full_command:
            st.error(f"Command '{command}' not found. Make sure it's installed and in your PATH.")
            if command == 'npx':
                st.error("Node.js may not be installed or properly configured. Install Node.js from https://nodejs.org")
            return {"tools": [], "resources": [], "prompts": []}
        
        # Use the full path to the command
        command = full_command
        
        server_params = StdioServerParameters(
            command=command,
            args=args or [],
            env=env or {}
        )
        print(f"Connecting to server with command: {command} and args: {args}")
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # List tools
                tools_result = await session.list_tools()
                
                # Try to list resources and prompts
                try:
                    resources_result = await session.list_resources()
                    resources = resources_result.resources if hasattr(resources_result, 'resources') else []
                except Exception:
                    resources = []
                
                try:
                    prompts_result = await session.list_prompts()
                    prompts = prompts_result.prompts if hasattr(prompts_result, 'prompts') else []
                except Exception:
                    prompts = []
                
                return {
                    "tools": tools_result.tools if hasattr(tools_result, 'tools') else [],
                    "resources": resources,
                    "prompts": prompts
                }
    except Exception as e:
        st.error(f"Error connecting to server: {str(e)}")
        return {"tools": [], "resources": [], "prompts": []}

async def call_tool(command, args, tool_name, tool_args):
    """Call a specific tool and return the result"""
    try:
        # Find the full path to the command
        full_command = find_executable(command)
        if not full_command:
            return f"Error: Command '{command}' not found. Make sure it's installed and in your PATH."
        
        # Use the full path to the command
        command = full_command
        
        server_params = StdioServerParameters(
            command=command,
            args=args or [],
            env={}
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Call the tool
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

def get_markdown_files(docs_folder):
    """Get list of markdown files in the docs folder"""
    docs_path = Path(docs_folder)
    if not docs_path.exists() or not docs_path.is_dir():
        return []
    
    return sorted([f for f in docs_path.glob('*.md')])
