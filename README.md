# Term Sheet Generator

This application helps you generate term sheets based on your requirements using AI. It processes natural language prompts to create professionally formatted term sheets for various funding scenarios.

## Features

- Generate term sheets from natural language descriptions
- Support for different funding rounds (Series A, B, C, SAFE, Convertible Notes)
- Validation of term sheet content
- Export to both text and DOCX formats
- User-friendly Streamlit interface

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
uv pip install -r requirements.txt
```

3. Create a `.env` file with your OpenAI API key:

```
OPENAI_API_KEY=your_api_key_here
```

## Usage

### Command Line

Run the example script:

```bash
python example.py
```

### Streamlit UI

Run the Streamlit application:

```bash
streamlit run streamlit_app.py
```

This will open a web interface where you can:
1. Enter your term sheet requirements in natural language
2. Select output format (Text only or Text and DOCX)
3. Choose whether to validate the term sheet
4. Select the AI model to use
5. Generate and download the term sheet

## Project Structure

- `agents/`: Contains the specialized AI agents for different tasks
  - `intent_parser.py`: Parses natural language into structured intent
  - `template_agent.py`: Selects and populates appropriate templates
  - `refinement_agent.py`: Refines the generated content
  - `validation_agent.py`: Validates the term sheet for issues
- `templates/`: Contains term sheet templates for different scenarios
- `utils/`: Utility functions
  - `docx_generator.py`: Converts text to DOCX format
- `main.py`: Core processing logic
- `streamlit_app.py`: Streamlit web interface
- `example.py`: Example usage script

## Example Prompt

```
Draft a $5M Series A term sheet with 20% discount and 1x non-participating liquidation preference for a SaaS company with a $20M valuation cap. Include 1 board seat for investors and pro rata rights.
```