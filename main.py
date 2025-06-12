#!/usr/bin/env python
"""Term Sheet Drafting Assistant

This script orchestrates the workflow between different agents to generate a term sheet
based on a natural language prompt.
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, Optional, Tuple
from dotenv import load_dotenv

# Import agents
from agents.intent_parser import IntentParsingAgent
from agents.template_agent import TemplateAgent
from agents.refinement_agent import RefinementAgent
from agents.validation_agent import ValidationAgent

# Import utilities
from utils.docx_generator import text_to_docx


def setup_environment() -> None:
    """Set up the environment for the application."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Create necessary directories if they don't exist
    os.makedirs("templates", exist_ok=True)
    os.makedirs("output", exist_ok=True)


def process_prompt(prompt: str, model_name: str = "gpt-4", 
                  generate_docx: bool = True, 
                  validate: bool = True) -> Tuple[str, Optional[str], Optional[str]]:
    """Process a natural language prompt to generate a term sheet.

    Args:
        prompt: The natural language prompt
        model_name: The name of the language model to use
        generate_docx: Whether to generate a DOCX document
        validate: Whether to validate the term sheet

    Returns:
        A tuple containing the term sheet text, validation report (if any), and path to DOCX (if generated)
    """
    print(f"\n[1/4] Parsing intent from prompt: '{prompt}'")
    intent_agent = IntentParsingAgent(model_name=model_name)
    structured_intent = intent_agent.parse(prompt)
    print(f"Extracted intent: {json.dumps(structured_intent, indent=2)}")
    
    print("\n[2/4] Selecting and populating template")
    template_agent = TemplateAgent()
    draft_content = template_agent.process(structured_intent)
    print(f"Template selected and populated with {len(draft_content)} characters")
    
    print("\n[3/4] Refining content")
    refinement_agent = RefinementAgent(model_name=model_name)
    refined_content = refinement_agent.process(draft_content, structured_intent)
    print(f"Content refined with {len(refined_content)} characters")
    
    validation_report = None
    if validate:
        print("\n[4/4] Validating term sheet")
        validation_agent = ValidationAgent(model_name=model_name)
        issues, validation_report = validation_agent.process(refined_content)
        if issues:
            print(f"Found {len(issues)} potential issues in the term sheet")
        else:
            print("No issues found in the term sheet")
    else:
        print("\n[4/4] Validation skipped")
    
    # Save the term sheet as a text file
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    text_output_path = os.path.join(output_dir, "term_sheet.txt")
    with open(text_output_path, "w", encoding="utf-8") as f:
        f.write(refined_content)
    print(f"\nTerm sheet saved to {text_output_path}")
    
    # Save validation report if available
    if validation_report:
        validation_path = os.path.join(output_dir, "validation_report.md")
        with open(validation_path, "w", encoding="utf-8") as f:
            f.write(validation_report)
        print(f"Validation report saved to {validation_path}")
    
    # Generate DOCX if requested
    docx_path = None
    if generate_docx:
        docx_path = os.path.join(output_dir, "term_sheet.docx")
        text_to_docx(refined_content, docx_path)
        print(f"DOCX document generated at {docx_path}")
    
    return refined_content, validation_report, docx_path


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Term Sheet Drafting Assistant")
    parser.add_argument("prompt", nargs="?", help="Natural language prompt for the term sheet")
    parser.add_argument("--model", "-m", default="gpt-4", help="Language model to use")
    parser.add_argument("--no-docx", action="store_true", help="Skip DOCX generation")
    parser.add_argument("--no-validation", action="store_true", help="Skip validation")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    # Set up the environment
    setup_environment()
    
    if args.interactive:
        print("=== Term Sheet Drafting Assistant (Interactive Mode) ===")
        while True:
            prompt = input("\nEnter your prompt (or 'exit' to quit): ")
            if prompt.lower() in ["exit", "quit", "q"]:
                break
                
            try:
                process_prompt(
                    prompt, 
                    model_name=args.model, 
                    generate_docx=not args.no_docx,
                    validate=not args.no_validation
                )
            except Exception as e:
                print(f"Error processing prompt: {e}")
    else:
        if not args.prompt:
            parser.print_help()
            return
            
        print("=== Term Sheet Drafting Assistant ===")
        try:
            process_prompt(
                args.prompt, 
                model_name=args.model, 
                generate_docx=not args.no_docx,
                validate=not args.no_validation
            )
        except Exception as e:
            print(f"Error processing prompt: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()