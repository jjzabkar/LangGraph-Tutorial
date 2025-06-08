from typing import Annotated, Literal
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from pydantic import BaseModel, Field


# from dotenv import load_dotenv
# from langgraph.graph import StateGraph, START, END
# from langchain.chat_models import init_chat_model
# from langchain_core.chat_history import InMemoryChatMessageHistory
# from src.agents.logical_agent_node import logical_agent_node
# from src.agents.router_node import router_node
# from src.agents.therapist_agent_node import therapist_agent_node



class State(TypedDict):
    messages: Annotated[list, add_messages]
    message_type: str | None

class MessageClassifier(BaseModel):
    message_type: Literal["emotional", "logical"] = Field(
        ...,
        description="Classify if the message requires an emotional (therapist) or logical response."
    )
