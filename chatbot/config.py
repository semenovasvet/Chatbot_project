EMBEDDING_MODEL = "text-embedding-ada-002"
DATASET_PATH = "productData.csv"

NUMBER_OF_RECOMMENDED_PRODUCTS = 5

# defaults for ask_gpt function
LANGUAGE_MODEL = "gpt-3.5-turbo"
# LANGUAGE_MODEL = "gpt-4"
TEMPERATURE = 0.5

# defaults for isEnd function
IS_END_DEFAULT_MODEL = "gpt-3.5-turbo"
IS_END_DEFAULT_TEMPERATURE = 0
IS_END_DEFAULT_CONTEXT = "Return only boolean value. Return True if this message sounds like a finish of the conversation. Return False otherwise."
