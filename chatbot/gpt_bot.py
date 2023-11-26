from django.shortcuts import render
from django.http import JsonResponse
import openai
import os
from dotenv import load_dotenv
import pandas as pd
from . import config
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

load_dotenv()


def chatbot(request):
    if request.method == "POST":
        message = request.POST.get("message")
        response = ask_gpt(message)
        return JsonResponse({"message": message, "response": response})
    elif request.method == "GET":
        return render(request, 'chatbot.html')


def ask_gpt(message):
    openai.api_key = os.environ['OPENAI_API_KEY']

    # response = openai.ChatCompletion.create(
    # model="gpt-3.5-turbo",
    # messages=[
    #     {"role": "system", "content": "Du bist ein hilfreicher Assistent auf der Website eines E-Commerce-Unternehmens, das gesundheitsbezogene Produkte verkauft"},
    #     {"role": "user", "content": message},
    # ],
    # max_tokens=30
    # )
    response = find_embedding(message)
    # return response["choices"][0]["message"]["content"]
    return response

def find_embedding(query):
    df = pd.read_csv(config.DATASET_PATH)
    embeddingsDict = pd.read_pickle(config.EMBEDDING_CASH_PATH)
    chroma_client = chromadb.PersistentClient()
    embedding_function = OpenAIEmbeddingFunction(api_key=os.environ.get('OPENAI_API_KEY'), model_name=config.EMBEDDING_MODEL)
    products_collection = chroma_client.get_or_create_collection(name='products_collection', embedding_function=embedding_function )
    
    results = products_collection.query(query_texts=query, n_results=5, include=['distances'])
    titles = [df["title"][ind] for ind in [int(i) for i in results['ids'][0]]]
    response = '<br>'.join(titles)
    return "<p> Hier sind die Produkte, die am besten zu Ihrer Anfrage passen: <br>" + response + "</p"

