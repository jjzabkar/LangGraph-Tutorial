from langchain_google_genai import ChatGoogleGenerativeAI
import dotenv
import logging
import os
from src.agents import State
from src.agents.util import get_message_content_with_context

dotenv.load_dotenv()

logger = logging.getLogger(__name__)


logger.info('Initializing Gemini LLM...')
# https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/metrics
_gemini_llm =ChatGoogleGenerativeAI(
        model=os.getenv('GEMINI_API_MODEL_NAME','gemini-2.5-flash-preview-04-17'),
        temperature=os.getenv('MUSIC_AGENT_MODEL_TEMPERATURE', 1.0),
        max_retries=2,
        api_key=os.getenv("GEMINI_API_KEY"),
    )
logger.info('Initialized Gemini LLM')


def music_agent_node(state: State):
    messages = [
        {"role": "system",
         "content": """You are a music-obsessed assistant. 
            Provide any answer, as long as it rhymes. If possible, ensure the answer has a poetic rhythm.
            Keep it brief and do not ramble on.
            Do not worry about inaccuracies.
            If more context is required, assume the previous questions and answers are relevant."""
         },
        {
            "role": "user",
            "content": get_message_content_with_context(state)
        }
    ]

    reply = _gemini_llm.invoke(messages)

    return {"messages": [{"role": "assistant", "content": reply.content}]}
