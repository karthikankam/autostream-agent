"""
tools.py
--------
Defines the mock_lead_capture tool for the AutoStream agent.

In LangGraph, a "tool" is just a Python function that the LLM can decide to call.
We use @tool decorator from LangChain to register it.
The LLM sees the function name + docstring and knows what it does and when to use it.
"""

from langchain_core.tools import tool


def mock_lead_capture(name: str, email: str, platform: str) -> str:
    """
    Captures a qualified lead after collecting all required information.
    This simulates saving the lead to a CRM or database.
    
    Args:
        name: Full name of the lead
        email: Email address of the lead  
        platform: Creator platform (YouTube, Instagram, TikTok, etc.)
    
    Returns:
        Success confirmation message
    """
    # In a real system, this would call a CRM API (HubSpot, Salesforce, etc.)
    print(f"\n{'='*50}")
    print(f"✅ LEAD CAPTURED SUCCESSFULLY!")
    print(f"   Name     : {name}")
    print(f"   Email    : {email}")
    print(f"   Platform : {platform}")
    print(f"{'='*50}\n")
    
    return f"Lead captured successfully for {name} ({email}) on {platform}. Our team will reach out within 24 hours!"
