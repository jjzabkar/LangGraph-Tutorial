from typing import Annotated, Literal
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from pydantic import BaseModel, Field


class State(TypedDict):
    messages: Annotated[list, add_messages]
    message_type: str | None

class MessageClassifier(BaseModel):
    message_type: Literal[
        "emotional",
        "logical",
        "music"
    ] = Field(
        ...,
        description="Classify if the message requires a musical, emotional (therapist), or logical response."
    )
