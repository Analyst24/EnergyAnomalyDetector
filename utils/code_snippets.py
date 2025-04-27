"""
Code snippet utilities for displaying and copying code in the Energy Anomaly Detection System
"""
import streamlit as st
import uuid
import re

def escape_js_string(code_str):
    """
    Escape a string for safe use in JavaScript
    
    Args:
        code_str (str): The code string to escape
        
    Returns:
        str: Escaped string safe for JavaScript
    """
    # Replace backslashes first (important to do this first)
    escaped = code_str.replace('\\', '\\\\')
    
    # Replace quotes and backticks
    escaped = escaped.replace('`', '\\`')
    escaped = escaped.replace("'", "\\'")
    escaped = escaped.replace('"', '\\"')
    
    # Replace newlines with explicit newline chars
    escaped = escaped.replace('\n', '\\n')
    
    # Replace tabs
    escaped = escaped.replace('\t', '\\t')
    
    # Replace carriage returns
    escaped = escaped.replace('\r', '\\r')
    
    return escaped

def display_code_with_copy_button(code, language="python", height=None):
    """
    Display a code snippet with a copy button
    
    Args:
        code (str): The code snippet to display
        language (str): The programming language for syntax highlighting
        height (int, optional): Custom height for the code block
    """
    # Generate a unique ID for this code block
    snippet_id = f"code_snippet_{uuid.uuid4().hex[:8]}"
    
    # Create a container for the code block
    container = st.container()
    
    with container:
        # Remove leading/trailing whitespace
        code = code.strip()
        
        # Escape the code for JavaScript
        escaped_code = escape_js_string(code)
        
        # Create copy button container with custom styling
        copy_button_html = f"""
        <div class="code-header" style="position: relative; margin-bottom: -40px; z-index: 10;">
            <button 
                id="copy_button_{snippet_id}" 
                style="position: absolute; top: 5px; right: 5px; 
                       background-color: rgba(70, 70, 70, 0.8); color: white; 
                       border: none; border-radius: 4px; padding: 5px 10px; 
                       font-size: 12px; cursor: pointer;"
                onclick="copyCode_{snippet_id}()">
                Copy
            </button>
        </div>
        """
        
        st.markdown(copy_button_html, unsafe_allow_html=True)
        
        # Display the code using streamlit code component
        st.code(code, language=language)
        
        # Add the JavaScript for copying to clipboard
        # This uses both clipboard API and fallback for offline use
        copy_script = f"""
        <script>
        function copyCode_{snippet_id}() {{
            const text = `{escaped_code}`;
            const button = document.getElementById('copy_button_{snippet_id}');
            
            // Try to use Clipboard API first
            if (navigator.clipboard && window.isSecureContext) {{
                navigator.clipboard.writeText(text).then(function() {{
                    button.innerHTML = 'Copied!';
                    button.style.backgroundColor = 'rgba(40, 167, 69, 0.8)';
                    
                    setTimeout(function() {{
                        button.innerHTML = 'Copy';
                        button.style.backgroundColor = 'rgba(70, 70, 70, 0.8)';
                    }}, 2000);
                }}).catch(function(err) {{
                    // If Clipboard API fails, try fallback
                    fallbackCopyTextToClipboard(text);
                }});
            }} else {{
                // Use fallback for offline environment
                fallbackCopyTextToClipboard(text);
            }}
            
            // Fallback copy function for offline use
            function fallbackCopyTextToClipboard(text) {{
                const textArea = document.createElement("textarea");
                textArea.value = text;
                
                // Make the textarea out of viewport
                textArea.style.position = "fixed";
                textArea.style.left = "-999999px";
                textArea.style.top = "-999999px";
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                
                try {{
                    const successful = document.execCommand('copy');
                    button.innerHTML = successful ? 'Copied!' : 'Failed!';
                    button.style.backgroundColor = successful ? 
                        'rgba(40, 167, 69, 0.8)' : 'rgba(220, 53, 69, 0.8)';
                }} catch (err) {{
                    button.innerHTML = 'Failed!';
                    button.style.backgroundColor = 'rgba(220, 53, 69, 0.8)';
                    console.error('Fallback: Oops, unable to copy', err);
                }}
                
                document.body.removeChild(textArea);
                
                setTimeout(function() {{
                    button.innerHTML = 'Copy';
                    button.style.backgroundColor = 'rgba(70, 70, 70, 0.8)';
                }}, 2000);
            }}
        }}
        </script>
        """
        
        st.markdown(copy_script, unsafe_allow_html=True)

def display_snippet_card(title, code, description=None, language="python", height=None):
    """
    Display a code snippet in a card format with a copy button
    
    Args:
        title (str): Title of the code snippet
        code (str): The code snippet to display
        description (str, optional): Description text to show before the code
        language (str): The programming language for syntax highlighting
        height (int, optional): Custom height for the code block
    """
    # Create a card-like container
    st.markdown(f"""
    <div style="background-color: #2C3E50; 
                border-radius: 5px; 
                padding: 10px; 
                margin-bottom: 20px;">
        <h3 style="margin-top: 0;">{title}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if description:
        st.markdown(description)
    
    # Display the code with copy button
    display_code_with_copy_button(code, language, height)

def offline_copy_js():
    """
    Return the JavaScript needed for offline clipboard functionality
    without using any external libraries
    """
    return """
    <script>
    // Add clipboard.js equivalent functionality for offline use
    function copyToClipboard(text) {
        // Create a temporary textarea element
        const textArea = document.createElement('textarea');
        textArea.value = text;
        
        // Make it invisible
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        
        // Select and copy
        textArea.focus();
        textArea.select();
        
        let success = false;
        try {
            success = document.execCommand('copy');
        } catch (err) {
            console.error('Error copying text: ', err);
        }
        
        // Clean up
        document.body.removeChild(textArea);
        return success;
    }
    </script>
    """