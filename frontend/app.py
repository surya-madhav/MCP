import streamlit as st
import os
import sys

# Add the parent directory to the Python path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from frontend.utils import default_config_path, check_node_installations

# Set page config
st.set_page_config(
    page_title="MCP Dev Tools",
    page_icon="🔌",
    layout="wide"
)

# Initialize session state
if 'debug_messages' not in st.session_state:
    st.session_state.debug_messages = []
    
if 'config_path' not in st.session_state:
    st.session_state.config_path = default_config_path

if 'servers' not in st.session_state:
    st.session_state.servers = {}

if 'active_server' not in st.session_state:
    st.session_state.active_server = None

def add_debug_message(message):
    """Add a debug message to the session state"""
    st.session_state.debug_messages.append(message)
    # Keep only the last 10 messages
    if len(st.session_state.debug_messages) > 10:
        st.session_state.debug_messages = st.session_state.debug_messages[-10:]

# Main app container
st.title("🔌 MCP Dev Tools")
st.write("Explore and interact with Model Control Protocol (MCP) servers")

# Sidebar for configuration and debug
with st.sidebar:
    st.title("MCP Dev Tools")
    
    # Node.js status
    st.subheader("Environment Status")
    node_info = check_node_installations()
    
    # Display Node.js status
    if node_info['node']['installed']:
        st.success(f"✅ Node.js {node_info['node']['version']}")
    else:
        st.error("❌ Node.js not found")
        st.markdown("[Install Node.js](https://nodejs.org/)")
    
    # Display npm status
    if node_info['npm']['installed']:
        st.success(f"✅ npm {node_info['npm']['version']}")
    else:
        st.error("❌ npm not found")
    
    # Display npx status
    if node_info['npx']['installed']:
        st.success(f"✅ npx {node_info['npx']['version']}")
    else:
        st.error("❌ npx not found")
        
    # Warning if Node.js components are missing
    if not all(info['installed'] for info in node_info.values()):
        st.warning("⚠️ Some Node.js components are missing. MCP servers that depend on Node.js (using npx) will not work.")
    
    # Debug information section at the bottom of sidebar
    st.divider()
    st.subheader("Debug Information")
    
    # Display debug messages
    if st.session_state.debug_messages:
        for msg in st.session_state.debug_messages:
            st.text(msg)
    else:
        st.text("No debug messages")
        
    # Clear debug messages button
    if st.button("Clear Debug Messages"):
        st.session_state.debug_messages = []
        st.rerun()

# Add a message for pages selection
st.info("Select a page from the sidebar to get started")

# Add welcome info
st.markdown("""
## Welcome to MCP Dev Tools

This tool helps you explore and interact with Model Control Protocol (MCP) servers. You can:

1. View and connect to available MCP servers
2. Explore tools, resources, and prompts provided by each server 
3. Configure and manage server connections

Select an option from the sidebar to get started.
""")

# Footer
st.divider()
st.write("MCP Dev Tools | Built with Streamlit")
