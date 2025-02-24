# import json

# from langchain_core.messages import ToolMessage

from langgraph.graph import END

from langchain_community.tools.tavily_search import TavilySearchResults

from src.state import State
from src.util import set_sensitive_env


def get_tools(type: str):
    if type == "search":
        set_sensitive_env("TAVILY_API_KEY")
        return TavilySearchResults(max_results=2)
    else:
        print(f"Invalid tool type requested: {type} - skipping")
        return None


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
