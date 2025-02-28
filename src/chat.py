import os

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

from src.state import State
from src.util import set_sensitive_env
from src.tools import get_tools

# this is a static config for LLMs
# we can add an env var for the exact model vs
# the vendor
LLMS = {
    "anthropic": "claude-3-5-sonnet-20240620",
    "openai": "gpt-4o",
}


def _get_llm(model: str):
    if model == "anthropic":
        set_sensitive_env("ANTHROPIC_API_KEY")
        return ChatAnthropic(model=LLMS["anthropic"])
    elif model == "openai":
        set_sensitive_env("OPENAI_API_KEY")
        return ChatOpenAI(model=LLMS["openai"])
    else:
        raise ValueError(f"Invalid model provided: {model}")


def chatbot(state: State):
    llm = _get_llm(os.environ["CHAT_MODEL"])

    tools = get_tools(["search", "human_assistance"])

    tooled_llm = llm.bind_tools(tools)

    message = tooled_llm.invoke(state["messages"])

    # from Langraph tut:
    #   Because we will be interrupting during tool execution,
    #   we disable parallel tool calling to avoid repeating any
    #   tool invocations when we resume.
    assert len(message.tool_calls) <= 1

    return {"messages": [message]}
