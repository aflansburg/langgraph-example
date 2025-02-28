import os
from typing import Callable
from langgraph.graph import END

from langchain_community.tools.tavily_search import TavilySearchResults

from langchain_core.tools import tool

from langgraph.types import Command, interrupt

from src.state import State
from src.util import set_sensitive_env

ENABLED_TOOLS = ["search", "human_assistance"]

# Tools


@tool
def human_assistance(query: str) -> str:
    """
    Use this tool to get help from a human.

    Args:
        query: The query to get help with.

    Returns:
        The response from the human.
    """
    human_response = interrupt({"query": query})
    return human_response["data"]


def _get_search_tool() -> Callable:
    """
    A search engine optimized for comprehensive, accurate, and trusted results.
    Useful for when you need to answer questions about current events.
    Input should be a search query.
    """
    set_sensitive_env("TAVILY_API_KEY")
    if not os.environ.get("TAVILY_API_KEY"):
        raise ValueError("TAVILY_API_KEY is not set and search tool will not function.")
    return TavilySearchResults(max_results=2)


# Tool Control

TOOL_REGISTRY = {
    "search": _get_search_tool,
    "human_assistance": human_assistance,
}


def get_tools(tool_types: list[str]) -> list[Callable]:
    tools = []
    for tool_type in tool_types:
        if tool_type in TOOL_REGISTRY:
            tool = TOOL_REGISTRY[tool_type]
            tools.append(tool)
        else:
            print(f"Tool type {tool_type} is not enabled - skipping")
    return tools


def route_tools(state: State):
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return END


# unused and replaced by builtin ToolNode
# but gives an idea of how to implement a custom tool node
# class BasicToolNode:
#     def __init__(self, tools: list) -> None:
#         self.tools_by_name = {tool.name: tool for tool in tools}

#     def __call__(self, inputs: dict):
#         if messages := inputs.get("messages", []):
#             message = messages[-1]
#         else:
#             raise ValueError("No messages provided")

#         outputs = []

#         for tool_call in message.tool_calls:
#             tool_result = self.tools_by_name[tool_call["name"]].invoke(
#                 tool_call["args"]
#             )
#             outputs.append(
#                 ToolMessage(
#                     content=json.dumps(tool_result),
#                     name=tool_call["name"],
#                     tool_call_id=tool_call["id"],
#                 )
#             )

#         return {"messages": outputs}
