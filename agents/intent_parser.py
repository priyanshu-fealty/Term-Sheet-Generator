import re
import json
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class IntentParsingAgent:
    """Agent for parsing user intent from natural language prompts."""
    
    def __init__(self, model_name: str = "gpt-4"):
        """Initialize the intent parsing agent.
        
        Args:
            model_name: The name of the language model to use.
        """
        self.llm = ChatOpenAI(model=model_name)
        
        # Define the prompt template for extracting structured information
        self.prompt_template = ChatPromptTemplate.from_template(
            """Extract structured information from the following prompt about a term sheet:
            
            {prompt}
            
            Extract the following information in JSON format:
            - type: The type of investment (e.g., Series A, Series B, SAFE, Convertible Note)
            - amount: The investment amount (e.g., $5M, $10M)
            - discount: Any discount mentioned (e.g., 20%)
            - liquidation_preference: Liquidation preference multiple (e.g., 1x, 2x)
            - participation: Whether there's participation (true/false)
            - valuation_cap: Any valuation cap mentioned (e.g., $20M)
            - board_seats: Number of board seats for investors
            - pro_rata: Whether pro rata rights are included (true/false)
            
            Return ONLY the JSON object without any additional text.
            """
        )
    
    def parse(self, prompt: str) -> Dict[str, Any]:
        """Parse the user's prompt to extract structured information.
        
        Args:
            prompt: The natural language prompt from the user.
            
        Returns:
            A dictionary containing the extracted information.
        """
        # First try rule-based parsing
        intent = self._rule_based_parsing(prompt)
        
        # If rule-based parsing didn't extract enough information, use LLM
        if len(intent) < 2:  # Arbitrary threshold
            intent = self._llm_based_parsing(prompt)
        
        return intent
    
    def _rule_based_parsing(self, prompt: str) -> Dict[str, Any]:
        """Use regex and rules to extract information from the prompt.
        
        Args:
            prompt: The natural language prompt from the user.
            
        Returns:
            A dictionary containing the extracted information.
        """
        intent = {}
        
        # Extract type
        type_patterns = [
            r"series\s+([a-c])",
            r"(safe)",
            r"(convertible\s+note)"
        ]
        
        for pattern in type_patterns:
            match = re.search(pattern, prompt.lower())
            if match:
                intent["type"] = match.group(1)
                break
        
        # Extract amount - improved pattern to handle various formats
        amount_match = re.search(r"\$(\d+(?:\.\d+)?\s*[KMB])", prompt) or re.search(r"\$(\d+(?:\.\d+)?)\s*([KMB])", prompt)
        if amount_match:
            # Handle different regex match groups based on which pattern matched
            if len(amount_match.groups()) == 1:
                # First pattern matched
                amount = amount_match.group(1)
                if not amount.startswith('$'):
                    amount = f"${amount}"
            else:
                # Second pattern matched
                amount = f"${amount_match.group(1)}{amount_match.group(2)}"
            intent["amount"] = amount
        
        # Extract discount
        discount_match = re.search(r"(\d+(?:\.\d+)?)\s*%\s*discount", prompt)
        if discount_match:
            intent["discount"] = f"{discount_match.group(1)}%"
        
        # Extract liquidation preference
        liq_pref_match = re.search(r"(\d+(?:\.\d+)?)x\s+(?:non-participating\s+)?liquidation\s+preference", prompt.lower())
        if liq_pref_match:
            intent["liquidation_preference"] = f"{liq_pref_match.group(1)}x"
            intent["participation"] = "non-participating" not in prompt.lower()
        
        # Extract valuation cap
        val_cap_match = re.search(r"\$(\d+(?:\.\d+)?\s*[KMB])\s+valuation\s+cap", prompt.lower())
        if val_cap_match:
            intent["valuation_cap"] = f"${val_cap_match.group(1)}"
        
        # Extract board seats
        board_match = re.search(r"(\d+)\s+board\s+seat", prompt.lower())
        if board_match:
            intent["board_seats"] = int(board_match.group(1))
        
        # Extract pro rata rights
        if "pro\s+rata" in prompt.lower():
            intent["pro_rata"] = True
        
        return intent
    
    def _llm_based_parsing(self, prompt: str) -> Dict[str, Any]:
        """Use LLM to extract information from the prompt.
        
        Args:
            prompt: The natural language prompt from the user.
            
        Returns:
            A dictionary containing the extracted information.
        """
        chain = self.prompt_template | self.llm
        response = chain.invoke({"prompt": prompt})
        
        try:
            # Extract JSON from the response
            json_str = response.content
            intent = json.loads(json_str)
            return intent
        except (json.JSONDecodeError, AttributeError):
            # Fallback to minimal intent if JSON parsing fails
            return {"type": "series_a"}  # Default to Series A