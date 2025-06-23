import logging
import os

import dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import OllamaEmbeddings
from vanna.pgvector.pgvector import PG_VectorStore

dotenv.load_dotenv()


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MyVannaPGVectorStore(PG_VectorStore):

    def __init__(self, config=None):

        ollama_model = os.getenv("OLLAMA_EMBEDDINGS_MODEL_NAME")
        logger.info(f"initialize Ollama Embedding Function with model {ollama_model}")
        self.embedding_function = OllamaEmbeddings(model=ollama_model)

        self.config = config or {
            'connection_string' : os.getenv("PG_VANNA_VECTOR_DB_CONNECTION_STRING"),
            'embedding_function' : self.embedding_function,
            'n_results': 10,
        }
        self.temperature = float(os.getenv("PG_VANNA_MODEL_TEMPERATURE", 0.7))

        logger.info(f"initialize Gemini API chat model")
        self.gemini_api_chat_model = ChatGoogleGenerativeAI(
            api_key=os.getenv("GEMINI_API_KEY"),
            model=os.getenv('GEMINI_API_MODEL_NAME'),
            temperature=self.temperature,
            max_retries=2,
        )

        super().__init__(self.config)

    def user_message(self, message: str) -> any:
        return {"role": "user", "content": message}

    def assistant_message(self, message: str) -> any:
        return {"role": "assistant", "content": message}

    def system_message(self, message):
        return {"role": "system", "content": message}

    def submit_prompt(self, prompt, **kwargs) -> str:
        logger.info(f"submit prompt to Gemini API chat model: {prompt}")
        response = self.gemini_api_chat_model.invoke(
            prompt,
            generation_config={
                "temperature": self.temperature,
            },
        )
        logger.info('extracting sql from LLM response')
        sql = self.extract_sql(response.content)
        logger.info(f'sql= {sql}')
        sql_valid = self.is_sql_valid(sql) and 'SELECT' in sql
        if sql_valid:
            return response.content
        else:
            logger.error('invalid sql')
            raise Exception('Invalid SQL')
