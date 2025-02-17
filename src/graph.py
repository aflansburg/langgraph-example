from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition

from src.chat import chatbot
from src.state import State
from src.tools import BasicToolNode, get_tools


def init_graph_builder() -> StateGraph:
    graph_builder = StateGraph(State)

    return graph_builder


def get_graph(requested_tools: list):
    graph_builder = init_graph_builder()

    graph_builder.add_node("chatbot", chatbot)

    tools = [get_tools(t) for t in requested_tools if get_tools(t)]

    graph_builder.add_node("tools", BasicToolNode(tools=tools))

    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition,
    )

    graph_builder.add_edge("tools", "chatbot")

    graph_builder.set_entry_point("chatbot")

    graph = graph_builder.compile()

    return graph


def stream_graph_updates(graph: StateGraph, user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)
