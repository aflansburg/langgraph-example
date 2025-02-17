from src.util import set_env
from src.graph import get_graph, stream_graph_updates


def main():
    set_env("CHAT_MODEL")

    # allows us to search the web
    # we can also add more tools here but we need
    # to implement them in src.tools.get_tools currently
    requested_tools = ["search"]

    graph = get_graph(requested_tools)

    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("User requested to quit. Here are the messages from state:")
                print(graph.get_state())

                break

            stream_graph_updates(graph=graph, user_input=user_input)
        except Exception as e:
            print(f"Error: {e}")
            break


if __name__ == "__main__":
    main()
