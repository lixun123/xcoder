"""
Search tools for LangChain Agent
"""

import os
from langchain.tools import tool
from langchain_community.utilities import SerpAPIWrapper

@tool
def web_search(query: str) -> str:
    """Perform a web search using SerpAPI.

    Args:
        query: Search query
    """
    # Ensure the SERPAPI_API_KEY is set in your environment variables
    if not os.getenv("SERPAPI_API_KEY"):
        return "SerpAPI API key not found. Please set the SERPAPI_API_KEY environment variable."

    try:
        search = SerpAPIWrapper()
        result = search.run(query)
        return result
    except Exception as e:
        return f"Web search failed: {str(e)}"
