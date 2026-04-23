"""Cura simple LangGraph agent."""

import os
import threading
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig
from langchain_mistralai import ChatMistralAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph


class AgentState(TypedDict):
    """State for the Cura agent."""

    messages: Annotated[list[BaseMessage], add_messages]


def _get_llm(config: RunnableConfig) -> ChatMistralAI:
    """Build a Mistral chat model from runtime config (BYOK)."""
    configurable = dict((config or {}).get("configurable") or {})

    user_key = (
        configurable.get("api_key") or os.getenv("MISTRAL_API_KEY") or ""
    ).strip()
    if not user_key:
        raise ValueError(
            "Missing API key. Provide configurable.api_key or set MISTRAL_API_KEY."
        )

    model = str(configurable.get("model") or "mistral-large-latest").strip()

    return ChatMistralAI(
        api_key=user_key,
        model=model,
    )


def chat_node(state: AgentState, config: RunnableConfig) -> dict:
    """Call the LLM with the current message history."""
    llm = _get_llm(config)
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


def build_agent() -> CompiledStateGraph:
    """Build and compile the LangGraph agent."""
    builder = StateGraph(AgentState)
    builder.add_node("chat", chat_node)
    builder.add_edge(START, "chat")
    builder.add_edge("chat", END)
    return builder.compile()


_GRAPH: CompiledStateGraph | None = None
_GRAPH_LOCK = threading.Lock()


def get_graph() -> CompiledStateGraph:
    """Return the compiled graph, building it once on first call."""
    global _GRAPH  # pylint: disable=global-statement
    if _GRAPH is None:
        with _GRAPH_LOCK:
            if _GRAPH is None:
                _GRAPH = build_agent()
    return _GRAPH


def __getattr__(name: str) -> object:
    if name == "graph":
        return get_graph()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
