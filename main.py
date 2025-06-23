import logging
import uuid

from dotenv import load_dotenv

from src.agents.graph_builder import my_graph
from src.util.mermaid import create_mermaid_diagram_files

load_dotenv()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)

create_mermaid_diagram_files()
logger.info('updated mermaid diagram')

def run_chatbot_synchronous():
    state = {"messages": [], "message_type": None}

    while True:
        user_input = input("Message: ")
        if user_input == "exit":
            logger.info("Bye")
            break

        state["messages"] = state.get("messages", []) + [
            {"role": "user", "content": user_input}
        ]

        state = my_graph.invoke(state)

        if state.get("messages") and len(state["messages"]) > 0:
            last_message = state["messages"][-1]
            logger.info(f"Assistant: {last_message.content}")

def run_chatbot_streaming():
    session_id = uuid.uuid4()
    config = {"configurable": {"session_id": session_id}}

    inputs = {"messages": [], "message_type": None}
    while True:
        user_input = input("\n🎯🎯Message: ")
        if user_input == "exit" or user_input == "q":
            logger.info("Bye")
            break
        inputs['messages'].append(user_input)
        # https://langchain-ai.lang.chat/langgraph/how-tos/streaming/#streaming-api
        for chunk in my_graph.stream(inputs, config, stream_mode="messages"):
            print(chunk[0].content, end="", flush=True)


if __name__ == "__main__":
    run_chatbot_streaming()
