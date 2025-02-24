from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition
from langgraph.prebuilt import ToolNode

from src.chat import chatbot
from src.state import State
from src.tools import get_tools
from src.memory import get_checkpointer


def init_graph_builder() -> StateGraph:
    graph_builder = StateGraph(State)

    return graph_builder


def get_graph(requested_tools: list):
    graph_builder = init_graph_builder()

    graph_builder.add_node("chatbot", chatbot)

    tools: list[any] = [get_tools(t) for t in requested_tools if get_tools(t)]

    tool_node = ToolNode(tools=tools)

    graph_builder.add_node("tools", tool_node)

    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition,
    )

    graph_builder.add_edge("tools", "chatbot")

    graph_builder.set_entry_point("chatbot")

    checkpointer = get_checkpointer(kind="in_memory")

    graph = graph_builder.compile(checkpointer=checkpointer)

    return graph


def stream_graph_updates(
    graph: StateGraph, user_input: str, init_config: dict[str, any]
):
    try:
        events = graph.stream(
            {"messages": [{"role": "user", "content": user_input}]},
            config=init_config,
            stream_mode="values",
        )
        for event in events:
            event["messages"][-1].pretty_print()
    except Exception as e:
        print(f"Error in stream_graph_updates: {e}")
