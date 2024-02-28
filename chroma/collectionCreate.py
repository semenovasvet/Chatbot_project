import chromadb
import openai
import logging
from dotenv import load_dotenv
import os

from . import config

load_dotenv()

from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
chroma_client = chromadb.PersistentClient()

import pandas as pd
df = pd.read_csv(config.DATASET_PATH)

if os.getenv("OPENAI_API_KEY") is not None:
    openai.api_key = os.environ['OPENAI_API_KEY']
    logging.info("OPENAI_API_KEY is ready")
else:
    logging.warning("OPENAI_API_KEY environment variable not found")


embedding_function = OpenAIEmbeddingFunction(api_key=os.environ.get('OPENAI_API_KEY'), model_name=config.EMBEDDING_MODEL)


products_collection = chroma_client.delete_collection (name='products_collection')
products_collection = chroma_client.get_or_create_collection(name='products_collection', embedding_function=embedding_function )


ids = []
strings = []
for ind in df.index:
    ids.append(f"{ind}")
    strings.append(f"{df['title'][ind]}, type: {df['type'][ind]}, info: {df['body'][ind]}")

products_collection.add(
    documents=strings,
    ids=ids
)