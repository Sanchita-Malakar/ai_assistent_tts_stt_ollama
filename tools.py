from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper


# -------- Web Search (DuckDuckGo) --------
duckduckgo = DuckDuckGoSearchRun()

@tool
def web_search(query: str) -> str:
    """Search the internet for current information. Use for recent events, news, or real-time data."""
    try:
        result = duckduckgo.run(query)
        return result[:500]  # Limit output
    except Exception as e:
        return f"Search failed: {str(e)}"


# -------- Wikipedia Search --------
wikipedia = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=1000)
)

@tool
def wikipedia_search(query: str) -> str:
    """Search Wikipedia for factual/historical info. Use for established facts, not current events."""
    try:
        result = wikipedia.run(query)
        return result[:800]  # Limit output
    except Exception as e:
        return f"Wikipedia search failed: {str(e)}"


# -------- Tool List --------
tools = [
    web_search,
    wikipedia_search,
]
