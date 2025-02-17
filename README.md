This is a fully fleshed out example of the [LangGraph tutorial](https://langchain-ai.github.io/langgraph/tutorials/introduction)

## Setup
1. Install uv from [here](https://docs.astral.sh/uv/getting-started/installation/)
2. Create a virtual environment
```bash
uv venv
```
3. Install the dependencies
```bash
uv sync
```
4. Run the script
```bash
uv run python main.py
```

## Note
It might be easier to set the environment variables up front, otherwise you'll be prompted for them every time you run it.
```bash
export OPENAI_API_KEY="..."
export ANTHROPIC_API_KEY="..."
export MODEL_NAME="gpt-4o"
export TAVILY_API_KEY="..."

# or
OPENAI_API_KEY="..." \
ANTHROPIC_API_KEY="..." \
MODEL_NAME="gpt-4o" \
TAVILY_API_KEY="..." \
uv run python main.py
```
Keep in mind you really only need one LLM API key.
