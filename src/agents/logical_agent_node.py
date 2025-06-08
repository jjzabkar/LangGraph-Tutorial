from src.agents import State
from src.agents.util import get_message_content_with_context
from src.chat.service.llm_chat_model_service import llm


def logical_agent_node(state: State):

    messages = [
        {"role": "system",
         "content": """You are a purely logical assistant. Focus only on facts and information.
            Provide clear, concise answers based on logic and evidence.
            Do not address emotions or provide emotional support.
            Be direct and straightforward in your responses.
            If more context is required, assume the previous questions and answers are relevant."""
         },
        {
            "role": "user",
            "content": get_message_content_with_context(state)
        }
    ]
    reply = llm.invoke(messages)
    return {"messages": [{"role": "assistant", "content": reply.content}]}
