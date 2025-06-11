from langchain.chat_models import init_chat_model

llm = init_chat_model(
    "deepseek-r1", model_provider="ollama"
    # "anthropic:claude-3-5-sonnet-latest"
    # 'google_anthropic_vertex'    -> langchain-google-vertexai
    # "google_vertexai:gemini-2.5-flash". ## NB: Assumes Vertex AI; use genAI SDK API instead
)

print(f'initialized LLM chat model {llm.model_config}')
