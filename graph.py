from typing import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage

from agent.llm import llm, SYSTEM_PROMPT
from agent.tools import tools


# ---- State ----
class AgentState(TypedDict):
    messages: list


# ---- LLM Node ----
def llm_node(state: AgentState):
    messages = state["messages"]
    
    # Add system prompt if not present
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
    
    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(tools)
    response = llm_with_tools.invoke(messages)
    
    return {"messages": state["messages"] + [response]}


# ---- Tool Node ----
tool_node = ToolNode(tools)


# ---- Build Graph ----
graph = StateGraph(AgentState)

graph.add_node("llm", llm_node)
graph.add_node("tools", tool_node)

graph.set_entry_point("llm")

graph.add_conditional_edges(
    "llm",
    lambda state: "tools" if state["messages"][-1].tool_calls else END,
)

graph.add_edge("tools", "llm")

# Compile the graph
app = graph.compile()