from langgraph.checkpoint.memory import MemorySaver


# in memory checkpointer
def get_checkpointer(kind: str = "in_memory"):
    if kind == "in_memory":
        return MemorySaver()
    else:
        raise ValueError(
            f"Invalid checkpointer type provided to `get_checkpointer`: {kind}"
        )
