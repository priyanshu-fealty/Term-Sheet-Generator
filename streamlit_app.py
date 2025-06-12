import streamlit as st
import os
import base64
from main import setup_environment, process_prompt

# Setup page configuration
st.set_page_config(
    page_title="Term Sheet Generator",
    page_icon="📄",
    layout="wide"
)

# Initialize environment
setup_environment()

# Function to get binary file content for download
def get_binary_file_downloader_html(file_path, file_label='File'):
    with open(file_path, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(file_path)}">{file_label}</a>'

# Function to get text file content for download
def get_text_file_downloader_html(file_path, file_label='File'):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = f.read()
    b64 = base64.b64encode(data.encode()).decode()
    return f'<a href="data:text/plain;base64,{b64}" download="{os.path.basename(file_path)}">{file_label}</a>'

# App title and description
st.title("Term Sheet Generator")
st.markdown("""
    This application helps you generate term sheets based on your requirements.
    Simply enter your specifications in natural language and get a professionally formatted term sheet.
""")

# User input section
st.header("Enter Your Requirements")
prompt = st.text_area(
    "Describe the term sheet you need (e.g., funding round, valuation, preferences, etc.)",
    height=150,
    placeholder="Example: Draft a $5M Series A term sheet with 20% discount and 1x non-participating liquidation preference for a SaaS company with a $20M valuation cap. Include 1 board seat for investors and pro rata rights."
)

# Format selection
st.subheader("Output Format")
output_format = st.radio(
    "Select the output format",
    options=["Text and DOCX", "Text Only"],
    index=0
)

generate_docx = output_format == "Text and DOCX"

# Validation option
validate = st.checkbox("Validate the term sheet", value=True)

# Model selection
model_name = st.selectbox(
    "Select AI Model",
    options=["gpt-4", "gpt-3.5-turbo"],
    index=0
)

# Generate button
if st.button("Generate Term Sheet", type="primary"):
    if not prompt:
        st.error("Please enter your requirements before generating a term sheet.")
    else:
        with st.spinner("Generating your term sheet..."):
            try:
                # Process the prompt
                term_sheet, validation_report, docx_path = process_prompt(
                    prompt=prompt,
                    model_name=model_name,
                    generate_docx=generate_docx,
                    validate=validate
                )
                
                # Display success message
                st.success("Term sheet generated successfully!")
                
                # Display the term sheet
                st.subheader("Generated Term Sheet")
                st.text_area("Term Sheet Content", term_sheet, height=400)
                
                # Download options
                st.subheader("Download Options")
                col1, col2 = st.columns(2)
                
                # Text download option
                with col1:
                    text_path = os.path.join("output", "term_sheet.txt")
                    st.markdown(get_text_file_downloader_html(text_path, "Download as Text"), unsafe_allow_html=True)
                
                # DOCX download option (if generated)
                if generate_docx and docx_path:
                    with col2:
                        st.markdown(get_binary_file_downloader_html(docx_path, "Download as DOCX"), unsafe_allow_html=True)
                
                # Display validation report if available
                if validation_report:
                    st.subheader("Validation Report")
                    st.markdown(validation_report)
            
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Footer
st.markdown("---")
st.markdown("© 2025 Term Sheet Generator | Powered by AI")