import os
import json
import streamlit as st
import asyncio
import sys

# Add the parent directory to the Python path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from frontend.utils import load_config, connect_to_server, call_tool, default_config_path

st.title("My Active MCP Servers")

# Configuration and server selection in the sidebar
with st.sidebar:
    st.subheader("Configuration")
    
    # Config file path input with unique key
    config_path = st.text_input(
        "Path to config file", 
        value=st.session_state.get('config_path', default_config_path),
        key="config_path_input_sidebar"
    )
    
    # Update the session state with the new path
    st.session_state.config_path = config_path
    
    if st.button("Load Servers", key="load_servers_sidebar"):
        if os.path.exists(config_path):
            config_data = load_config(config_path)
            if config_data and 'mcpServers' in config_data:
                st.session_state.config_data = config_data
                st.session_state.servers = config_data.get('mcpServers', {})
                
                # Add debug message
                message = f"Found {len(st.session_state.servers)} MCP servers in config"
                if 'debug_messages' in st.session_state:
                    st.session_state.debug_messages.append(message)
                
                st.success(message)
            else:
                error_msg = "No MCP servers found in config"
                if 'debug_messages' in st.session_state:
                    st.session_state.debug_messages.append(error_msg)
                st.error(error_msg)
        else:
            error_msg = f"Config file not found: {config_path}"
            if 'debug_messages' in st.session_state:
                st.session_state.debug_messages.append(error_msg)
            st.error(error_msg)
    
    # Server selection dropdown
    st.divider()
    st.subheader("Server Selection")
    
    if 'servers' in st.session_state and st.session_state.servers:
        server_names = list(st.session_state.servers.keys())
        selected_server = st.selectbox(
            "Select an MCP server", 
            server_names,
            key="server_selection_sidebar"
        )
        
        if st.button("Connect", key="connect_button_sidebar"):
            server_config = st.session_state.servers.get(selected_server, {})
            command = server_config.get('command')
            args = server_config.get('args', [])
            env = server_config.get('env', {})
            
            with st.spinner(f"Connecting to {selected_server}..."):
                # Add debug message
                debug_msg = f"Connecting to {selected_server}..."
                if 'debug_messages' in st.session_state:
                    st.session_state.debug_messages.append(debug_msg)
                
                # Connect to the server
                server_info = asyncio.run(connect_to_server(command, args, env))
                st.session_state[f'server_info_{selected_server}'] = server_info
                st.session_state.active_server = selected_server
                
                # Add debug message about connection success/failure
                if server_info.get('tools'):
                    success_msg = f"Connected to {selected_server}: {len(server_info['tools'])} tools"
                    if 'debug_messages' in st.session_state:
                        st.session_state.debug_messages.append(success_msg)
                else:
                    error_msg = f"Connected but no tools found"
                    if 'debug_messages' in st.session_state:
                        st.session_state.debug_messages.append(error_msg)
                
                # Force the page to refresh to show connected server details
                st.rerun()
    else:
        st.info("Load config to see servers")

# Main area: Only display content when a server is connected
if 'active_server' in st.session_state and st.session_state.active_server:
    active_server = st.session_state.active_server
    server_info_key = f'server_info_{active_server}'
    
    if server_info_key in st.session_state:
        st.subheader(f"Connected to: {active_server}")
        
        server_info = st.session_state[server_info_key]
        server_config = st.session_state.servers.get(active_server, {})
        
        # Display server configuration
        with st.expander("Server Configuration"):
            st.json(server_config)
        
        # Display tools
        if server_info.get('tools'):
            st.subheader("Available Tools")
            
            # Create tabs for each tool
            tool_tabs = st.tabs([tool.name for tool in server_info['tools']])
            
            for i, tool in enumerate(server_info['tools']):
                with tool_tabs[i]:
                    st.markdown(f"**Description:** {tool.description or 'No description provided'}")
                    
                    # Tool schema
                    if hasattr(tool, 'inputSchema') and tool.inputSchema:
                        with st.expander("Input Schema"):
                            st.json(tool.inputSchema)
                        
                        # Generate form for tool inputs
                        st.subheader("Call Tool")
                        
                        # Create a form
                        with st.form(key=f"tool_form_{active_server}_{tool.name}"):
                            # Fix duplicate ID error by adding unique keys for form fields
                            tool_inputs = {}
                            
                            # Check if input schema has properties
                            if 'properties' in tool.inputSchema:
                                # Create form inputs based on schema properties
                                for param_name, param_schema in tool.inputSchema['properties'].items():
                                    param_type = param_schema.get('type', 'string')
                                    
                                    # Create unique key for each form field
                                    field_key = f"{active_server}_{tool.name}_{param_name}"
                                    
                                    if param_type == 'string':
                                        tool_inputs[param_name] = st.text_input(
                                            f"{param_name}", 
                                            help=param_schema.get('description', ''),
                                            key=field_key
                                        )
                                    elif param_type == 'number' or param_type == 'integer':
                                        tool_inputs[param_name] = st.number_input(
                                            f"{param_name}", 
                                            help=param_schema.get('description', ''),
                                            key=field_key
                                        )
                                    elif param_type == 'boolean':
                                        tool_inputs[param_name] = st.checkbox(
                                            f"{param_name}", 
                                            help=param_schema.get('description', ''),
                                            key=field_key
                                        )
                                    # Add more types as needed
                            
                            # Submit button
                            submit_button = st.form_submit_button(f"Execute {tool.name}")
                            
                            if submit_button:
                                # Get server config
                                command = server_config.get('command')
                                args = server_config.get('args', [])
                                
                                with st.spinner(f"Executing {tool.name}..."):
                                    # Add debug message
                                    if 'debug_messages' in st.session_state:
                                        st.session_state.debug_messages.append(f"Executing {tool.name}")
                                    
                                    # Call the tool
                                    result = asyncio.run(call_tool(command, args, tool.name, tool_inputs))
                                    
                                    # Display result
                                    st.subheader("Result")
                                    st.write(result)
                    else:
                        st.warning("No input schema available for this tool")
        
        # Display resources if any
        if server_info.get('resources'):
            with st.expander("Resources"):
                for resource in server_info['resources']:
                    st.write(f"**{resource.name}:** {resource.uri}")
                    if hasattr(resource, 'description') and resource.description:
                        st.write(resource.description)
                    st.divider()
        
        # Display prompts if any
        if server_info.get('prompts'):
            with st.expander("Prompts"):
                for prompt in server_info['prompts']:
                    st.write(f"**{prompt.name}**")
                    if hasattr(prompt, 'description') and prompt.description:
                        st.write(prompt.description)
                    st.divider()
    else:
        st.info(f"Server {active_server} is selected but not connected. Click 'Connect' in the sidebar.")
else:
    # Initial state when no server is connected
    st.info("Select a server from the sidebar and click 'Connect' to start interacting with it.")
