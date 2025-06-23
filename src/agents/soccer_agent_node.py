import logging

import dotenv

from src.agents import State
from src.agents.util import get_message_content_with_context
from src.vanna.vanna_service import get_vanna

dotenv.load_dotenv()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

vanna = get_vanna()

def soccer_agent_node(state: State):
    question = get_message_content_with_context(state)
    logger.info(f"Ask Vanna: {question}\n")
    sql, sql_results_df, _plotly = vanna.ask(question, visualize=False, auto_train=False, print_results=False, allow_llm_to_see_data=True)
    content = 'No results found.'

    if sql_results_df is not None:
        content = sql_results_df.to_html(index=False)

    logger.info(f"content= {content}")

    return {"messages": [{"role": "assistant", "content": content}]}
