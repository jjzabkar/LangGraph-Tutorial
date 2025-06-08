from src.agents import State
from src.agents.util import get_message_content_with_context
from src.chat.service.llm_chat_model_service import llm


def therapist_agent_node(state: State):
    messages = [
        {"role": "system",
         "content": """You are a compassionate therapist. Focus on the emotional aspects of the user's message.
                        Show empathy, validate their feelings, and help them process their emotions.
                        Ask thoughtful questions to help them explore their feelings more deeply.
                        Avoid giving logical solutions unless explicitly asked.
                        If more context is required, assume the previous questions and answers are relevant."""
         },
        {
            "role": "user",
            "content": get_message_content_with_context(state), # last_message.content
        }
    ]
    reply = llm.invoke(messages)
    return {"messages": [{"role": "assistant", "content": reply.content}]}
