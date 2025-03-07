import streamlit as st
import os
import sys
from pathlib import Path
import re

# Add the parent directory to the Python path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from frontend.utils import get_markdown_files

st.title("Documentation")

# Define the docs directory path
docs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "docs")

# Helper function to calculate the height for a mermaid diagram
def calculate_diagram_height(mermaid_code):
    # Count the number of lines in the diagram
    line_count = len(mermaid_code.strip().split('\n'))
    
    # Estimate the height based on complexity and type
    base_height = 100  # Minimum height
    
    # Add height based on the number of lines
    line_height = 30 if line_count <= 5 else 25  # Adjust per-line height based on total lines for density
    height = base_height + (line_count * line_height)
    
    # Extra height for different diagram types
    if "flowchart" in mermaid_code.lower() or "graph" in mermaid_code.lower():
        height += 50
    elif "sequenceDiagram" in mermaid_code:
        height += 100  # Sequence diagrams typically need more height
    elif "classDiagram" in mermaid_code:
        height += 75
    
    # Extra height for diagrams with many connections
    if mermaid_code.count("-->") + mermaid_code.count("<--") + mermaid_code.count("-.-") > 5:
        height += 100
    
    # Extra height if many items in diagram
    node_count = len(re.findall(r'\[[^\]]+\]', mermaid_code))
    if node_count > 5:
        height += node_count * 20
    
    return height

# Helper function to extract and render mermaid diagrams
def render_markdown_with_mermaid(content):
    # Regular expression to find mermaid code blocks
    mermaid_pattern = r"```mermaid\s*([\s\S]*?)\s*```"
    
    # Find all mermaid diagrams
    mermaid_blocks = re.findall(mermaid_pattern, content)
    
    # Replace mermaid blocks with placeholders
    content_with_placeholders = re.sub(mermaid_pattern, "MERMAID_DIAGRAM_PLACEHOLDER", content)
    
    # Split content by placeholders
    parts = content_with_placeholders.split("MERMAID_DIAGRAM_PLACEHOLDER")
    
    # Render each part with mermaid diagrams in between
    for i, part in enumerate(parts):
        if part.strip():
            st.markdown(part)
        
        # Add mermaid diagram after this part (if there is one)
        if i < len(mermaid_blocks):
            mermaid_code = mermaid_blocks[i]
            
            # Calculate appropriate height for this diagram
            diagram_height = calculate_diagram_height(mermaid_code)
            
            # Render mermaid diagram using streamlit components
            st.components.v1.html(
                f"""
                <div class="mermaid" style="margin: 20px 0;">
                {mermaid_code}
                </div>
                <script src="https://cdn.jsdelivr.net/npm/mermaid@9/dist/mermaid.min.js"></script>
                <script>
                    mermaid.initialize({{ 
                        startOnLoad: true,
                        theme: 'default',
                        flowchart: {{ 
                            useMaxWidth: false,
                            htmlLabels: true,
                            curve: 'cardinal'
                        }}
                    }});
                </script>
                """,
                height=diagram_height,
                scrolling=True
            )

# Check if docs directory exists
if not os.path.exists(docs_dir):
    st.error(f"Documentation directory not found: {docs_dir}")
else:
    # Get list of markdown files
    markdown_files = get_markdown_files(docs_dir)
    
    # Sidebar for document selection
    with st.sidebar:
        st.subheader("Select Document")
        
        if not markdown_files:
            st.info("No documentation files found")
        else:
            # Create options for the selectbox - use filenames without path and extension
            file_options = [f.stem for f in markdown_files]
            
            # Select document
            selected_doc = st.selectbox(
                "Choose a document", 
                file_options,
                format_func=lambda x: x.replace("-", " ").title(),
                key="doc_selection"
            )
            
            # Find the selected file path
            selected_file_path = next((f for f in markdown_files if f.stem == selected_doc), None)
            
            # Store selection in session state
            if selected_file_path:
                st.session_state["selected_doc_path"] = str(selected_file_path)

    # Display the selected markdown file
    if "selected_doc_path" in st.session_state:
        selected_path = st.session_state["selected_doc_path"]
        
        try:
            with open(selected_path, 'r') as f:
                content = f.read()
            
            # Set style for better code rendering
            st.markdown(
                """
                <style>
                code {
                    white-space: pre-wrap !important;
                }
                .mermaid {
                    text-align: center !important;
                }
                </style>
                """, 
                unsafe_allow_html=True
            )
            
            # Use the custom function to render markdown with mermaid
            render_markdown_with_mermaid(content)
            
        except Exception as e:
            st.error(f"Error loading document: {str(e)}")
    else:
        if markdown_files:
            # Display the first document by default
            try:
                with open(str(markdown_files[0]), 'r') as f:
                    content = f.read()
                
                # Use the custom function to render markdown with mermaid
                render_markdown_with_mermaid(content)
                
                # Store the selected doc in session state
                st.session_state["selected_doc_path"] = str(markdown_files[0])
            except Exception as e:
                st.error(f"Error loading default document: {str(e)}")
        else:
            st.info("Select a document from the sidebar to view documentation")
