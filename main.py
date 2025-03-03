from datetime import datetime
import sys
import os

from src.util import set_env
from src.graph import get_graph, stream_graph_updates, write_graph_png

if os.path.exists(".env.local"):
    import dotenv

    dotenv.load_dotenv(dotenv_path=".env.local")
    print(".env.local present - loaded env vars")


def main(
    write_graph_img: bool = False,
    store_incremental_state: bool = False,
    run_timestamp: str = "",
):
    set_env("CHAT_MODEL")

    # allows us to search the web
    # we can also add more tools here but we need
    # to implement them in src.tools.get_tools currently
    requested_tools = ["search", "human_assistance"]

    init_config = {"configurable": {"thread_id": "1"}}

    graph = get_graph(requested_tools)

    if write_graph_img:
        write_graph_png(graph)

    try:
        user_input = input("User: ")

        stream_graph_updates(
            graph=graph,
            user_input=user_input,
            init_config=init_config,
            store_incremental_state=store_incremental_state,
            run_timestamp=run_timestamp,
        )
    except Exception as e:
        print(f"Error in main loop: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    should_write_graph_img = "--graph-image" in sys.argv
    should_store_incremental_state = "--incremental-state" in sys.argv
    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    main(
        write_graph_img=should_write_graph_img,
        store_incremental_state=should_store_incremental_state,
        run_timestamp=run_timestamp,
    )
