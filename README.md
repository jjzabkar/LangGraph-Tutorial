# LangGraph-Tutorial

https://www.youtube.com/watch?v=aywZrzNaKjs

https://github.com/techwithtim/LangGraph-Tutorial

## Setup

### Gemini

Enable Google Gemini GenAI API.

Get `GEMINI_API_KEY` here: https://aistudio.google.com/app/apikey

### Local Ollama

Install GPU-enabled OSX Ollama via [download](https://ollama.com/download) or [Docker](https://hub.docker.com/r/ollama/ollama).

```bash
ollama pull deepseek-r1;
# or, change llm_chat_model_service:
ollama pull llama:3.2;
```

### UV

Install [UV](https://docs.astral.sh/uv/)

```basH
brew install uv;
```

### Dependencies

```bash
uv add \
  python-dotenv \
  langgraph \
  "langchain[anthropic,ollama]" \
  ipykernel \
  google-genai \
  langchain-google-genai \
  langchain-google-vertexai ;
```

## Extras

1. In-Memory chat history
2. Streams responses
3. Multiple agents