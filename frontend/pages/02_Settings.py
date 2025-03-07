import streamlit as st
import os
import json
import json5
import sys

# Add the parent directory to the Python path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from frontend.utils import default_config_path, load_config

st.title("Settings")

# Settings container
with st.container():
    st.subheader("Configuration Settings")
    
    # Get current config path from session state
    current_config_path = st.session_state.get('config_path', default_config_path)
    
    # Config file path selector (with unique key)
    config_path = st.text_input(
        "Path to Claude Desktop config file", 
        value=current_config_path,
        key="settings_config_path"
    )
    
    # Update the session state if path changed
    if config_path != current_config_path:
        st.session_state.config_path = config_path
        if 'debug_messages' in st.session_state:
            st.session_state.debug_messages.append(f"Config path updated to: {config_path}")
    
    # Add a button to view the current config
    if st.button("View Current Config", key="view_config_button"):
        if os.path.exists(config_path):
            with st.spinner("Loading config file..."):
                config_data = load_config(config_path)
                if config_data:
                    with st.expander("Config File Content", expanded=True):
                        st.json(config_data)
                    
                    # Update session state
                    st.session_state.config_data = config_data
                    if 'mcpServers' in config_data:
                        st.session_state.servers = config_data.get('mcpServers', {})
                        
                        # Add debug message
                        success_msg = f"Found {len(st.session_state.servers)} MCP servers in the config file"
                        if 'debug_messages' in st.session_state:
                            st.session_state.debug_messages.append(success_msg)
                else:
                    st.error("Failed to load config file")
        else:
            st.error(f"Config file not found: {config_path}")

# Help section for adding new servers
with st.expander("Adding New MCP Servers"):
    st.markdown("""
    ## How to Add New MCP Servers
    
    To add a new MCP server to your configuration:
    
    1. Edit the Claude Desktop config file (usually at `~/Library/Application Support/Claude/claude_desktop_config.json`)
    
    2. Add or modify the `mcpServers` section with your new server configuration:
    
    ```json
    "mcpServers": {
        "my-server-name": {
            "command": "python",
            "args": ["/path/to/your/server.py"],
            "env": {
                "OPTIONAL_ENV_VAR": "value"
            }
        },
        "another-server": {
            "command": "npx",
            "args": ["some-mcp-package"]
        }
    }
    ```
    
    3. Save the file and reload it in the MCP Dev Tools
    
    The `command` is the executable to run (e.g., `python`, `node`, `npx`), and `args` is an array of arguments to pass to the command.
    """)
