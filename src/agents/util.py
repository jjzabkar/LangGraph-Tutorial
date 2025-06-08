from src.agents import State


def get_message_content_with_context(state: State) -> str:
    last_message = state["messages"][-1]
    previous_messages = "\n".join(
        message.content for message in reversed(state['messages'][0:-1])
    )
    content = f'{last_message}'
    if previous_messages is not None and len(previous_messages) > 2:
        content = content + f'\nPrevious contextual messages, ordered by recent first: \n{previous_messages}'
    return content
