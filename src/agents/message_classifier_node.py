from src.agents import State, MessageClassifier
from src.chat.service.llm_chat_model_service import llm


def message_classifier_node(state: State):
    last_message = state["messages"][-1]
    classifier_llm = llm.with_structured_output(MessageClassifier)

    classification_prompt = """Classify the user message as either:
    - 'music': if it as for music, a song, pertains to music, rhythm, tone, or music-related topics
    - 'emotional': if it asks for emotional support, therapy, deals with feelings, or personal problems
    - 'logical': if it asks for facts, information, logical analysis, or practical solutions
    """

    result = classifier_llm.invoke([
        {"role": "system", "content": classification_prompt},
        {"role": "user", "content": last_message.content}
    ])
    return {"message_type": result.message_type}
