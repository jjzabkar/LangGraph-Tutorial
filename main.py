import uuid

from dotenv import load_dotenv
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langchain_core.chat_history import InMemoryChatMessageHistory

from pydantic import BaseModel, Field
from typing_extensions import TypedDict

load_dotenv()

llm = init_chat_model(
    "ollama:deepseek-r1"
    # "anthropic:claude-3-5-sonnet-latest"
)


class MessageClassifier(BaseModel):
    message_type: Literal["emotional", "logical"] = Field(
        ...,
        description="Classify if the message requires an emotional (therapist) or logical response."
    )


class State(TypedDict):
    messages: Annotated[list, add_messages]
    message_type: str | None


def classify_message(state: State):
    last_message = state["messages"][-1]
    classifier_llm = llm.with_structured_output(MessageClassifier)

    classification_prompt = """Classify the user message as either:
    - 'emotional': if it asks for emotional support, therapy, deals with feelings, or personal problems
    - 'logical': if it asks for facts, information, logical analysis, or practical solutions
    """

    result = classifier_llm.invoke([
        {"role": "system", "content": classification_prompt},
        {"role": "user", "content": last_message.content}
    ])
    return {"message_type": result.message_type}


def router(state: State):
    message_type = state.get("message_type", "logical")
    if message_type == "emotional":
        return {"next": "therapist"}

    return {"next": "logical"}

def get_message_content_with_context(state: State) -> str:
    last_message = state["messages"][-1]
    previous_messages = "\n".join(
        message.content for message in reversed(state['messages'][0:-1])
    )
    content = f'{last_message}'
    if previous_messages is not None and len(previous_messages) > 2:
        content = content + f'\nPrevious contextual messages, ordered by recent first: \n{previous_messages}'
    return content

def therapist_agent(state: State):
    messages = [
        {"role": "system",
         "content": """You are a compassionate therapist. Focus on the emotional aspects of the user's message.
                        Show empathy, validate their feelings, and help them process their emotions.
                        Ask thoughtful questions to help them explore their feelings more deeply.
                        Avoid giving logical solutions unless explicitly asked."""
         },
        {
            "role": "user",
            "content": get_message_content_with_context(state), # last_message.content
        }
    ]
    reply = llm.invoke(messages)
    return {"messages": [{"role": "assistant", "content": reply.content}]}


def logical_agent(state: State):

    messages = [
        {"role": "system",
         "content": """You are a purely logical assistant. Focus only on facts and information.
            Provide clear, concise answers based on logic and evidence.
            Do not address emotions or provide emotional support.
            Be direct and straightforward in your responses."""
         },
        {
            "role": "user",
            "content": get_message_content_with_context(state)
        }
    ]
    reply = llm.invoke(messages)
    return {"messages": [{"role": "assistant", "content": reply.content}]}


chats_by_session_id = {}
def get_chat_history(session_id: str) -> InMemoryChatMessageHistory:
    chat_history = chats_by_session_id.get(session_id)
    if chat_history is None:
        chat_history = InMemoryChatMessageHistory()
        chats_by_session_id[session_id] = chat_history
    return chat_history


graph_builder = StateGraph(State)
graph_builder.add_node("classifier", classify_message)
graph_builder.add_node("router", router)
graph_builder.add_node("therapist", therapist_agent)
graph_builder.add_node("logical", logical_agent)

graph_builder.add_edge(START, "classifier")
graph_builder.add_edge("classifier", "router")

graph_builder.add_conditional_edges(
    "router",
    lambda state: state.get("next"),
    {"therapist": "therapist", "logical": "logical"}
)

graph_builder.add_edge("therapist", END)
graph_builder.add_edge("logical", END)

graph = graph_builder.compile()


def run_chatbot_syncrhronous():
    state = {"messages": [], "message_type": None}

    while True:
        user_input = input("Message: ")
        if user_input == "exit":
            print("Bye")
            break

        state["messages"] = state.get("messages", []) + [
            {"role": "user", "content": user_input}
        ]

        state = graph.invoke(state)

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
        for chunk in graph.stream(inputs, config, stream_mode="messages"):
            print(chunk[0].content, end="", flush=True)


def run_chatbot_streaming_memory(state, config) -> list:
    # Make sure that config is populated with the session id
    if "configurable" not in config or "session_id" not in config["configurable"]:
        raise ValueError(
            "Make sure that the config includes the following information: {'configurable': {'session_id': 'some_value'}}"
        )
    # Fetch the history of messages and append to it any new messages.
    chat_history = get_chat_history(config["configurable"]["session_id"])
    messages = list(chat_history.messages) + state["messages"]

    run_chatbot_syncrhronous(chat_history)

    # Finally, update the chat message history to include
    # the new input message from the user together with the
    # response from the model.
    chat_history.add_messages(state["messages"] + [ai_message])
    # return {"messages": ai_message}


if __name__ == "__main__":
    run_chatbot_streaming()
