"""Cura CLI — interactive chat in the terminal."""

import os

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage

load_dotenv()

from cura.agent import get_graph  # noqa: E402  # pylint: disable=wrong-import-position


def main() -> None:
    """Start an interactive chat session in the terminal."""
    graph = get_graph()
    config = {"configurable": {"api_key": os.getenv("MISTRAL_API_KEY")}}
    messages = []

    print("Cura — tapez votre message, Ctrl+C pour quitter.\n")

    while True:
        try:
            user_input = input("Vous : ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nAu revoir.")
            break

        if not user_input:
            continue

        messages.append(HumanMessage(content=user_input))

        print("Cura : ", end="", flush=True)
        full_response = ""
        for chunk, _ in graph.stream(
            {"messages": messages},
            config=config,
            stream_mode="messages",
        ):
            print(chunk.content, end="", flush=True)
            full_response += chunk.content
        print("\n")

        messages.append(AIMessage(content=full_response))


if __name__ == "__main__":
    main()
