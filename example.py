import os
import sys
from dotenv import load_dotenv
from main import setup_environment, process_prompt

def main():
    # Load environment variables
    load_dotenv()
    setup_environment()
    
    # Example prompt
    prompt = "Draft a $5M Series A term sheet with 20% discount and 1x non-participating liquidation preference for a SaaS company with a $20M valuation cap. Include 1 board seat for investors and pro rata rights."
    
    # Process the prompt
    result = process_prompt(
        prompt=prompt,
        model="gpt-4",  # You can change this to a different model if needed
        generate_docx=True,
        validate=True,
        interactive=False
    )
    
    # Print the result
    print("\nGenerated Term Sheet:\n")
    print(result)
    print("\nA DOCX file has also been generated in the 'output' directory.")

if __name__ == "__main__":
    main()