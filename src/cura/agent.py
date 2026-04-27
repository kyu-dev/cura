"""Cura simple LangGraph agent."""

import os
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig
from langchain_mistralai import ChatMistralAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from cura.tools.web_loader import retrieve_blog_posts


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
    llm = _get_llm(config).bind_tools([retrieve_blog_posts])
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


_TOOLS = [retrieve_blog_posts]


def build_agent() -> CompiledStateGraph:
    """Build and compile the LangGraph agent."""
    builder = StateGraph(AgentState)
    builder.add_node("chat", chat_node)
    builder.add_node("tools", ToolNode(_TOOLS))
    builder.add_edge(START, "chat")
    builder.add_conditional_edges("chat", tools_condition)
    builder.add_edge("tools", "chat")
    return builder.compile()


graph = build_agent()
