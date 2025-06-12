"""Validation Agent

This agent flags high-risk clauses and potential issues in the term sheet.
"""

import re
from typing import Dict, Any, List, Tuple
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate


class ValidationAgent:
    """Agent that validates term sheets and flags high-risk clauses."""

    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.0):
        """Initialize the Validation Agent.

        Args:
            model_name: The name of the language model to use
            temperature: The temperature parameter for the language model
        """
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        self.prompt_template = ChatPromptTemplate.from_template(
            """You are an expert legal advisor specializing in venture capital term sheets.
            
            Review the following term sheet and identify any high-risk clauses or issues that should be flagged.
            Focus on identifying the following types of problematic clauses:
            
            1. Uncapped indemnity clauses
            2. Unilateral control provisions
            3. Unusual or excessive liquidation preferences
            4. Aggressive anti-dilution provisions
            5. Unreasonable vesting terms
            6. Problematic transfer restrictions
            7. Unusual or one-sided termination rights
            8. Any terms that deviate significantly from industry standards
            
            For each issue identified, provide:
            1. The specific clause or text that is problematic
            2. Why it's problematic
            3. A suggested improvement or alternative
            
            Term sheet to review:
            {term_sheet}
            
            Format your response as a JSON array of objects, each with "clause", "issue", and "suggestion" fields.
            If no issues are found, return an empty array.
            """
        )

    def validate(self, term_sheet: str) -> List[Dict[str, str]]:
        """Validate the term sheet and identify high-risk clauses.

        Args:
            term_sheet: The term sheet content to validate

        Returns:
            A list of identified issues with the term sheet
        """
        # First try rule-based validation for common issues
        issues = self._rule_based_validation(term_sheet)
        
        # Then use LLM for more comprehensive validation
        llm_issues = self._llm_based_validation(term_sheet)
        
        # Combine issues, avoiding duplicates
        seen_clauses = {issue["clause"] for issue in issues}
        for issue in llm_issues:
            if issue["clause"] not in seen_clauses:
                issues.append(issue)
                seen_clauses.add(issue["clause"])
                
        return issues

    def _rule_based_validation(self, term_sheet: str) -> List[Dict[str, str]]:
        """Use regex and rules to identify common issues.

        Args:
            term_sheet: The term sheet content to validate

        Returns:
            A list of identified issues
        """
        issues = []
        
        # Check for uncapped indemnity
        if re.search(r"indemnify.*without limitation|unlimited indemnity|uncapped indemnity", 
                    term_sheet, re.IGNORECASE | re.DOTALL):
            issues.append({
                "clause": "Uncapped Indemnity",
                "issue": "The term sheet contains uncapped indemnity provisions, which create unlimited liability.",
                "suggestion": "Add a cap on indemnity obligations, typically tied to the investment amount."
            })
        
        # Check for unusual liquidation preferences
        match = re.search(r"(\d+(?:\.\d+)?)\s*[xX]\s*(?:participating|liquidation)", term_sheet)
        if match and float(match.group(1)) > 1.5:
            issues.append({
                "clause": f"{match.group(1)}x Liquidation Preference",
                "issue": f"A {match.group(1)}x liquidation preference is higher than the standard 1x preference.",
                "suggestion": "Consider negotiating down to a 1x non-participating liquidation preference, which is industry standard."
            })
        
        # Check for full-ratchet anti-dilution
        if re.search(r"full.?ratchet|full.?ratchet\s+anti.?dilution", term_sheet, re.IGNORECASE):
            issues.append({
                "clause": "Full-Ratchet Anti-dilution",
                "issue": "Full-ratchet anti-dilution provisions are aggressive and can severely impact common shareholders.",
                "suggestion": "Consider a more balanced weighted average anti-dilution provision."
            })
        
        # Check for unusual vesting terms
        if re.search(r"vesting.{1,50}(5|6|7|8|9|10)\s+years", term_sheet, re.IGNORECASE):
            issues.append({
                "clause": "Extended Vesting Schedule",
                "issue": "The vesting schedule appears to be longer than the industry standard of 4 years.",
                "suggestion": "Consider a standard 4-year vesting schedule with a 1-year cliff."
            })
        
        return issues

    def _llm_based_validation(self, term_sheet: str) -> List[Dict[str, str]]:
        """Use LLM to identify issues in the term sheet.

        Args:
            term_sheet: The term sheet content to validate

        Returns:
            A list of identified issues
        """
        import json
        
        formatted_prompt = self.prompt_template.format_messages(term_sheet=term_sheet)
        response = self.llm(formatted_prompt)
        
        try:
            # Extract JSON from the response
            json_str = response.content.strip()
            # Handle case where the model might include markdown code block formatting
            if json_str.startswith("```json"):
                json_str = json_str.split("```json")[1]
            if json_str.endswith("```"):
                json_str = json_str.split("```")[0]
                
            issues = json.loads(json_str)
            return issues
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"Error parsing LLM response for validation: {e}")
            # Return empty list if parsing fails
            return []

    def format_issues_report(self, issues: List[Dict[str, str]]) -> str:
        """Format the identified issues into a readable report.

        Args:
            issues: The list of identified issues

        Returns:
            A formatted report of the issues
        """
        if not issues:
            return "No issues found. The term sheet appears to follow standard practices."
        
        report = "# Term Sheet Validation Report\n\n"
        report += f"**{len(issues)} issues identified:**\n\n"
        
        for i, issue in enumerate(issues, 1):
            report += f"## Issue {i}: {issue['clause']}\n\n"
            report += f"**Problem:** {issue['issue']}\n\n"
            report += f"**Suggestion:** {issue['suggestion']}\n\n"
            report += "---\n\n"
        
        return report

    def process(self, term_sheet: str) -> Tuple[List[Dict[str, str]], str]:
        """Process the term sheet with the validation agent.

        Args:
            term_sheet: The term sheet content to validate

        Returns:
            A tuple containing the list of issues and a formatted report
        """
        issues = self.validate(term_sheet)
        report = self.format_issues_report(issues)
        return issues, report


# Example usage
if __name__ == "__main__":
    agent = ValidationAgent()
    test_term_sheet = """
    TERM SHEET FOR SERIES A PREFERRED STOCK FINANCING OF
    EXAMPLE COMPANY, INC.
    
    Amount of Financing: $5M
    Valuation: $20M pre-money
    Liquidation Preference: 2x participating
    Anti-dilution: Full-ratchet
    
    Indemnification: The Company shall indemnify the Investors without limitation for any losses arising from breaches of representations and warranties.
    
    Vesting: 5-year vesting schedule for all employees with no cliff.
    """
    
    issues, report = agent.process(test_term_sheet)
    print(report)