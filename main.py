import uuid

from dotenv import load_dotenv

from src.agents.graph_builder import my_graph

load_dotenv()


def run_chatbot_synchronous():
    state = {"messages": [], "message_type": None}

    while True:
        user_input = input("Message: ")
        if user_input == "exit":
            print("Bye")
            break

        state["messages"] = state.get("messages", []) + [
            {"role": "user", "content": user_input}
        ]

        state = my_graph.invoke(state)

        if state.get("messages") and len(state["messages"]) > 0:
            last_message = state["messages"][-1]
            print(f"Assistant: {last_message.content}")

def run_chatbot_streaming():
    session_id = uuid.uuid4()
    config = {"configurable": {"session_id": session_id}}

    inputs = {"messages": [], "message_type": None}
    while True:
        user_input = input("Message: ")
        if user_input == "exit" or user_input == "q":
            print("Bye")
            break
        inputs['messages'].append(user_input)
        # https://langchain-ai.lang.chat/langgraph/how-tos/streaming/#streaming-api
        for chunk in my_graph.stream(inputs, config, stream_mode="messages"):
            print(chunk[0].content, end="", flush=True)


if __name__ == "__main__":
    run_chatbot_streaming()
