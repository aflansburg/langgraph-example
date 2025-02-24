import json
from datetime import datetime
from typing import Any, Union

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
    graph: StateGraph,
    user_input: str,
    init_config: dict[str, any],
    store_incremental_state: bool,
    run_timestamp: str,
):
    try:
        events = graph.stream(
            {"messages": [{"role": "user", "content": user_input}]},
            config=init_config,
            stream_mode="values",
        )
        for event in events:
            event["messages"][-1].pretty_print()

        if store_incremental_state:
            try:
                snapshot = graph.get_state(config=init_config)
            except Exception as e:
                print(
                    f"No state yet, or error getting state, or error serializing state - will write empty state: {e}"
                )

            try:
                file_name = f"local_state/incremental_state_{run_timestamp}.ndjson"

                with open(file_name, "a") as f:
                    values: Union[dict[str, Any], Any] = snapshot.values

                    json.dump(
                        {
                            "next_node": str(snapshot.next) if snapshot.next else "END",
                            "state": {
                                "values": str(values),
                                "config": str(snapshot.config),
                                "metadata": str(snapshot.metadata),
                                "created_at": str(snapshot.created_at),
                                "parent_config": str(snapshot.parent_config),
                                "tasks": str(snapshot.tasks),
                            },
                        },
                        f,
                    )
                    f.write("\n")
            except Exception as e:
                print(f"Error in writing incremental state: {e}")

    except Exception as e:
        print(f"Error in stream_graph_updates: {e}")


def write_graph_png(graph: StateGraph):
    try:
        with open("graph_img/graph.png", "wb") as f:
            f.write(graph.get_graph().draw_mermaid_png())
    except Exception as e:
        print(f"Error in when attempting to write graph png: {e}")
