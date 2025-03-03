import os
from typing import Any, Annotated, Callable
from langgraph.graph import END

from langchain_community.tools.tavily_search import TavilySearchResults

from langchain_core.tools import tool, InjectedToolCallId
from langchain_core.messages import ToolMessage
from langgraph.types import Command, interrupt

from src.state import State
from src.util import set_sensitive_env

ENABLED_TOOLS = ["search", "human_assistance"]

# Tools


@tool
def human_assistance(
    query: str,
    attributes: dict[str, Any] = {},
    tool_call_id: Annotated[str, InjectedToolCallId] = "",
) -> str:
    """
    Use this tool to get help from a human.
    You can provide arbitrary attributes to the human.
    The human will return a response with the following format:
    {
        "query": <query>,
        "OK to continue?": <yes|no>,
        <arbitrary attribute name>: <arbitrary attribute value>
    }

    Args:
        query: The query to get help with.
        attributes: Arbitrary attributes to pass to the human. If there is no need for attributes, pass an empty dictionary.
        tool_call_id: The ID of the tool call.
    Returns:
        The response from the human.
    """
    print(
        f"Human assistance called with query: {query} and attributes: {attributes} and tool_call_id: {tool_call_id}"
    )
    human_query_object = {"query": query}

    for k, v in attributes.items():
        human_query_object[k] = v

    print(f"Human query object: {human_query_object}")

    human_response = interrupt(human_query_object)

    print(f"Human response: {human_response}")

    if human_response.get("OK to continue?", "").lower().startswith("y"):
        response = "continue"
    else:
        corrected_attributes = {}
        for k, v in attributes.items():
            if k not in ["query", "OK to continue?"]:
                corrected_attributes[k] = human_response.get(k, v)
        response = f"Made corrections: {', '.join([f'{k}={v}' for k, v in corrected_attributes.items()])}"

    state_update = {
        "messages": [ToolMessage(response, tool_call_id=tool_call_id)],
    }

    for k, v in corrected_attributes.items():
        state_update[k] = v

    return Command(update=state_update)


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
