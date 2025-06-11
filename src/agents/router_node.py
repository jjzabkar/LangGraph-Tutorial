from src.agents import State


def router_node(state: State):
    message_type = state.get("message_type", "logical")
    if message_type == "music":
        return {"next": "music"}
    if message_type == "emotional":
        return {"next": "therapist"}

    return {"next": "logical"}
