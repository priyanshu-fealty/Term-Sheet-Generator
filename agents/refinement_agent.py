"""Refinement Agent

This agent polishes and enhances the generated term sheet content.
"""

from typing import Dict, Any, Optional
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate


class RefinementAgent:
    """Agent that refines and polishes the generated term sheet content."""

    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.2):
        """Initialize the Refinement Agent.

        Args:
            model_name: The name of the language model to use
            temperature: The temperature parameter for the language model
        """
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        self.prompt_template = ChatPromptTemplate.from_template(
            """You are an expert legal document editor specializing in term sheets for startup financing.
            
            I will provide you with a draft term sheet and the original structured intent. Your task is to:
            
            1. Ensure all terms from the intent are properly reflected in the document
            2. Improve the language for clarity and professionalism
            3. Add appropriate section headers and formatting
            4. Ensure the document follows standard term sheet conventions
            5. Make sure the document is complete and coherent
            
            Original intent: {intent}
            
            Draft term sheet:
            {draft_content}
            
            Please provide the refined term sheet:
            """
        )

    def refine(self, draft_content: str, intent: Dict[str, Any]) -> str:
        """Refine the draft term sheet content.

        Args:
            draft_content: The draft term sheet content
            intent: The original structured intent

        Returns:
            The refined term sheet content
        """
        # Convert intent to a readable string format for the prompt
        intent_str = ", ".join([f"{k}: {v}" for k, v in intent.items()])
        
        formatted_prompt = self.prompt_template.format_messages(
            intent=intent_str,
            draft_content=draft_content
        )
        
        response = self.llm(formatted_prompt)
        return response.content.strip()

    def add_headers_and_formatting(self, content: str) -> str:
        """Add headers and improve formatting of the term sheet.

        Args:
            content: The term sheet content

        Returns:
            The formatted term sheet content
        """
        # This is a simpler version that could be used without LLM
        # In practice, the refine method above handles this more comprehensively
        
        lines = content.split("\n")
        formatted_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                formatted_lines.append(line)
                continue
                
            # Identify potential headers (short lines that don't end with punctuation)
            if len(line) < 50 and not line[-1] in [".", ":", ",", ";"]:
                # Make it uppercase and add underline
                formatted_lines.append(line.upper())
                formatted_lines.append("="*len(line))
            else:
                formatted_lines.append(line)
        
        return "\n".join(formatted_lines)

    def process(self, draft_content: str, intent: Dict[str, Any]) -> str:
        """Process the draft content with the refinement agent.

        Args:
            draft_content: The draft term sheet content
            intent: The original structured intent

        Returns:
            The refined term sheet content
        """
        # First use the LLM to refine the content
        refined_content = self.refine(draft_content, intent)
        
        # If the LLM refinement fails or is unavailable, fall back to basic formatting
        if not refined_content or refined_content == draft_content:
            refined_content = self.add_headers_and_formatting(draft_content)
            
        return refined_content


# Example usage
if __name__ == "__main__":
    agent = RefinementAgent()
    test_intent = {
        "type": "Series A",
        "amount": "$5M",
        "discount": "20%",
        "liquidation": "1x non-participating"
    }
    test_draft = """
    TERM SHEET FOR SERIES A PREFERRED STOCK FINANCING OF
    [COMPANY NAME, INC.]
    
    Amount of Financing: $5M
    Discount: 20%
    Liquidation Preference: 1x non-participating
    
    This term sheet summarizes the principal terms of the proposed financing.
    """
    
    result = agent.process(test_draft, test_intent)
    print(result)