"""Template Agent

This agent selects and populates appropriate templates based on structured intent.
"""

import os
import json
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape


class TemplateAgent:
    """Agent that selects and populates templates based on structured intent."""

    def __init__(self, templates_dir: str = "templates"):
        """Initialize the Template Agent.

        Args:
            templates_dir: Directory containing the templates
        """
        self.templates_dir = templates_dir
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Ensure templates directory exists
        os.makedirs(templates_dir, exist_ok=True)

    def select_template(self, intent: Dict[str, Any]) -> str:
        """Select the appropriate template based on the intent.

        Args:
            intent: The structured intent

        Returns:
            The name of the selected template
        """
        # Default to Series A template if type is not specified
        term_sheet_type = intent.get("type", "").lower()
        
        if "safe" in term_sheet_type:
            return "safe.txt"
        elif "convertible note" in term_sheet_type:
            return "convertible_note.txt"
        elif "series b" in term_sheet_type:
            return "series_b.txt"
        elif "series c" in term_sheet_type:
            return "series_c.txt"
        else:
            # Default to Series A for any other type or if type is not specified
            return "series_a.txt"

    def populate_template(self, template_name: str, intent: Dict[str, Any]) -> str:
        """Populate the selected template with the structured intent.

        Args:
            template_name: The name of the template to use
            intent: The structured intent

        Returns:
            The populated template as a string
        """
        try:
            template = self.env.get_template(template_name)
            return template.render(**intent)
        except Exception as e:
            # If template doesn't exist or there's an error, use fallback template
            print(f"Error loading template {template_name}: {e}")
            return self._generate_fallback_template(intent)

    def process(self, intent: Dict[str, Any]) -> str:
        """Process the structured intent and generate a populated template.

        Args:
            intent: The structured intent

        Returns:
            The populated template as a string
        """
        template_name = self.select_template(intent)
        return self.populate_template(template_name, intent)

    def _generate_fallback_template(self, intent: Dict[str, Any]) -> str:
        """Generate a fallback template if the selected template is not available.

        Args:
            intent: The structured intent

        Returns:
            A basic populated template as a string
        """
        term_sheet_type = intent.get("type", "Series A")
        amount = intent.get("amount", "[AMOUNT]")
        
        fallback_template = f"""
        TERM SHEET FOR {term_sheet_type.upper()} PREFERRED STOCK FINANCING OF
        [COMPANY NAME, INC.]
        
        Amount of Financing: {amount}
        """
        
        # Add other terms if available
        if "valuation_cap" in intent:
            fallback_template += f"\nValuation Cap: {intent['valuation_cap']}"
        
        if "discount" in intent:
            fallback_template += f"\nDiscount: {intent['discount']}"
        
        if "liquidation" in intent:
            fallback_template += f"\nLiquidation Preference: {intent['liquidation']}"
        
        if "board_seats" in intent:
            fallback_template += f"\nBoard Seats: {intent['board_seats']}"
        
        if intent.get("pro_rata", False):
            fallback_template += "\nPro Rata Rights: Included"
        
        # Add other standard sections
        fallback_template += """
        
        This term sheet summarizes the principal terms of the proposed financing.
        
        [Additional standard terms would be included here based on the term sheet type.]
        """
        
        return fallback_template


# Example usage
if __name__ == "__main__":
    agent = TemplateAgent()
    test_intent = {
        "type": "Series A",
        "amount": "$5M",
        "discount": "20%",
        "liquidation": "1x non-participating"
    }
    result = agent.process(test_intent)
    print(result)