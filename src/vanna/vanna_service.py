import logging
import os

import dotenv
import requests

from src.vanna.my_pg_vectorstore import MyVannaPGVectorStore

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)

logger.info("load dotenv")
dotenv.load_dotenv()


def get_vanna():
    logger.info("initialize Vanna's MyPGVectorStore")
    vn = MyVannaPGVectorStore()

    logger.info("initialize Vanna's connection to target Postgres DB")
    vn.connect_to_postgres(
        host=os.getenv("TARGET_TEXT2SQL_PG_HOST"),
        dbname=os.getenv("TARGET_TEXT2SQL_PG_DATABASE"),
        user=os.getenv("TARGET_TEXT2SQL_PG_USER"),
        password=os.getenv("TARGET_TEXT2SQL_PG_PASSWORD"),
        port=os.getenv("TARGET_TEXT2SQL_PG_PORT"),
    )

    logger.info('introspect schema and omit system tables')
    df_information_schema = vn.run_sql("""SELECT * FROM INFORMATION_SCHEMA.COLUMNS
        WHERE table_name NOT ILIKE 'pg_%'
        and table_schema NOT IN ('information_schema', 'timescaledb_information', 'timescaledb_experimental')
        and table_schema NOT ILIKE '_timescaledb_%'
    """)

    logger.info("break up the information schema into bite-sized chunks that can be referenced by the LLM")
    plan = vn.get_training_plan_generic(df_information_schema)

    logger.info(f'train Vanna on the plan')
    vn.train(plan=plan)
    logger.info('done initializing Vanna')
    return vn
