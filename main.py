import sys

from src.util import set_env
from src.graph import get_graph, stream_graph_updates, write_graph_png


def main(write_graph_img: bool = False):
    set_env("CHAT_MODEL")

    # allows us to search the web
    # we can also add more tools here but we need
    # to implement them in src.tools.get_tools currently
    requested_tools = ["search"]

    init_config = {"configurable": {"thread_id": "1"}}

    graph = get_graph(requested_tools)

    if write_graph_img:
        write_graph_png(graph)

    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("User requested to quit. Here are the messages from state:")
                print(graph.get_state())

                break

            stream_graph_updates(
                graph=graph, user_input=user_input, init_config=init_config
            )
        except Exception as e:
            print(f"Error: {e}")
            break


if __name__ == "__main__":
    should_write_graph_img = False
    if len(sys.argv) > 1 and sys.argv[1] == "--graph-image":
        should_write_graph_img = True
    main(write_graph_img=should_write_graph_img)
