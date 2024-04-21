import chromadb
import openai
import logging
from dotenv import load_dotenv
import os
from . import config

load_dotenv()

""" This file serves for creating a collection of embeddings using chromadb library from a csv file
"""
# initializing chroma client
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
chroma_client = chromadb.PersistentClient()

# loading products dataset as pandas dataframe
import pandas as pd
df = pd.read_csv(config.DATASET_PATH)

# initialising openai module
if os.getenv("OPENAI_API_KEY") is not None:
    openai.api_key = os.environ['OPENAI_API_KEY']
    logging.info("OPENAI_API_KEY is ready")
else:
    logging.warning("OPENAI_API_KEY environment variable not found")

# defining the embedding function
embedding_function = OpenAIEmbeddingFunction(api_key=os.environ.get('OPENAI_API_KEY'), model_name=config.EMBEDDING_MODEL)

# first deleting already existing collection
products_collection = chroma_client.delete_collection (name='products_collection')

# creating new empty collection
products_collection = chroma_client.get_or_create_collection(name='products_collection', embedding_function=embedding_function )


""" Processing data from the dataset in chunks:
        - creating a list of ids and a corresponding list of strings containing product information
        - adding processed products data into the collection, embeddings generation is handled by chromadb.

    Chunks are implemented in order to avoid 'RateLimitError'.
"""

chunk_size = 1000  
for start in range(0, len(df), chunk_size):
    end = start + chunk_size
    ids = [f"{ind}" for ind in df.index[start:end]]
    strings = [f"{df['title'][ind]}, type: {df['type'][ind]}, info: {df['body'][ind]}" for ind in df.index[start:end]]
    
    products_collection.add(documents=strings, ids=ids)
    logging.info(f"Processed and added chunk {start//chunk_size + 1}")