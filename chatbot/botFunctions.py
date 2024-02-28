from django.shortcuts import render
from django.http import JsonResponse
import openai
import json, logging
import os
from dotenv import load_dotenv
import pandas as pd
from . import config
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from shopifyFunctions.trackingUrl import ShopifyTracking


load_dotenv()

class ChatBot:
    def __init__(self) -> None:
        self.df = pd.read_csv(config.DATASET_PATH)
        openai.api_key = os.environ['OPENAI_API_KEY']
        self.productsDict = {}
        self.completion_tokens = 0
        self.prompt_tokens = 0


    def main(self, request):
        logging.warning("Received dictionary: ", request.POST)
        if request.method == "POST" and request.POST.get("name")=="productDescription":
            message = request.POST.get("message")
            response = self.find_embedding(message)
            return JsonResponse({"message": message, "response": response})
        
        elif request.method == "POST" and request.POST.get("name")=="advice":
            message = request.POST.get("message")
            response, isEnd = self.ask_gpt(message)
            return JsonResponse({"message": message, "response": response, "isEnd": isEnd})

        elif request.method == "POST" and request.POST.get("name")=="salesOrderNumber":
            message = request.POST.get("message")
            response, isFound = self.find_salesOrder(message)
            return JsonResponse({"message": message, "response": response, "isFound": isFound})

        elif request.method == "POST" and request.POST.get("name")=="email":
            message = request.POST.get("message")
            response, isFound = self.find_customer(message)
            return JsonResponse({"message": message, "response": response, "isFound": isFound})
        
        elif request.method == "GET":
            return render(request, 'chatbot.html')


    def ask_gpt(self, message):
        response = openai.ChatCompletion.create(
        # model="gpt-3.5-turbo",
        model = "gpt-4",
        temperature = 0.5,
        messages=[
            {"role": "system", "content": f"Du bist ein hilfreicher Assistent auf der Website altruan.com. Gib kurze Antworten. Nutze die Informationen aus diesem Dictionary, um die Fragen der Nutzer zu den Produkten zu beantworten: {self.productsDict}. Wenn die Frage des Benutzers über die im Dictionary gefundenen Informationen hinausgeht, antworte, dass die Frage nicht in dein Fachgebiet fällt."},
            {"role": "user", "content": message},
        ]
        )
        if response:
            answer = response["choices"][0]["message"]["content"]
            isEnd = self.is_end(message)
            self.completion_tokens += int(response["usage"]["completion_tokens"])
            self.prompt_tokens += int(response["usage"]["prompt_tokens"])
            if isEnd == "False":
                return f'<p>{answer}</p>', False
            elif isEnd == "True":
                return f'<p>{answer} <br>Completion_tokens: {self.completion_tokens}.<br>Prompt_tokens: {self.prompt_tokens}</p>', True

        return "<p> Could not process the message</p>"
        

    def is_end(self, message):
        response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        temperature = 0,
        messages=[
            {"role": "system", "content": f"Return boolean value. Return True if this message sounds like a finish of the conversation"},
            {"role": "user", "content": message},
        ]
        )
        if response:
            isEnd = response["choices"][0]["message"]["content"]
            self.completion_tokens += int(response["usage"]["completion_tokens"])
            self.prompt_tokens += int(response["usage"]["prompt_tokens"])
            return isEnd


    def find_embedding(self, query):
        chroma_client = chromadb.PersistentClient()
        embedding_function = OpenAIEmbeddingFunction(api_key=os.environ.get('OPENAI_API_KEY'), model_name=config.EMBEDDING_MODEL)
        products_collection = chroma_client.get_or_create_collection(name='products_collection', embedding_function=embedding_function )
        
        results = products_collection.query(query_texts=query, n_results=5, include=['distances'])
        ids_list = [int(i) for i in results['ids'][0]]
        minId = self.find_the_cheapest(ids_list)
        titles = []
        for id in ids_list:
            self.productsDict[id] = {"id": self.df["id"][id],"title": self.df["title"][id], "body": self.df["body"][id], "type": self.df["type"][id], "price": self.df["price"][id], "endpoint": self.df["endpoint"][id]}
            titles.append(f'<p><a href=https://altruan.com/products/{self.df["endpoint"][id]} target="blank">{self.df["title"][id]}</a> - von {self.df["price"][id]} €</p>')

        response = '<br>'.join(titles)
        cheapestProduct = f'<p>Das billigste dieser Produkte ist <a href=https://altruan.com/products/{self.df["endpoint"][minId]} target="blank">{self.df["title"][minId]}</a></p>'
        return "<p> Hier sind die Produkte, die am besten zu Ihrer Anfrage passen: <br>" + response + "<br>" + cheapestProduct + "</p"


    def find_the_cheapest(self, ids_list):
        minPrice = 100000
        minId = None
        df = pd.read_csv(config.DATASET_PATH)
        for num in ids_list:
            price = float(df["price"][num])
            if price < minPrice:
                minPrice = price
                minId = num
        return minId


    def find_salesOrder(self, salesOrderNumber):
        responseDict = ShopifyTracking().find_by_number(salesOrderNumber=salesOrderNumber)
        if responseDict and responseDict["order"] == False:
            return  f'<p>Es wurde kein Kundenauftrag mit der Nummer {salesOrderNumber} gefunden. Bitte überprüfen Sie die Auftragsnummer und versuchen Sie es erneut.</p><button id="forgot-button" type="button" class="forgot-button" onclick="forgotNumber()" style="display:block">Ich habe die Auftragsnummer vergessen</button>', False
        elif responseDict and responseDict["order"] == True and not responseDict["urls"]:
            return  f'<p>Ihre Bestellung wurde noch nicht versandt</p>', True
        elif responseDict and responseDict["order"] == True and responseDict["urls"]:
            if len(responseDict["urls"]) == 1:
                return f'<p>Verwenden Sie diesen Link, um Ihre Bestellung zu verfolgen: <a href={responseDict["url"]} target="blank">Auftrag {salesOrderNumber}</a></p>', True
            else:
                linkString = ""
                for url in responseDict["urls"]:
                    linkString += f'<a href={url} target="blank">Auftrag {salesOrderNumber}</a><br>'
                return f'<p>Verwenden Sie diese Links, um Ihre Bestellung zu verfolgen:<br>{linkString}</p>', True


    def find_customer(self, email):
        trackingLinksDict, isFound = ShopifyTracking().find_by_email(email=email)
        if trackingLinksDict and isFound:
            linkString = ""
            for order in trackingLinksDict:
                linkString += f'<a href={trackingLinksDict[order]} target="blank">Auftrag {order}</a><br>'
            return f'<p>Hier sind alle bezahlten Aufträge, die ich gefunden habe:<br>{linkString}</p>', isFound
        elif not trackingLinksDict and isFound:
            return f'<p>Ihre Bestellung wurde noch nicht versandt</p>', isFound
        elif not isFound:
            return f'<p>Ich habe in den letzten 90 Tagen keine bezahlten Bestellungen für Kunden mit {email} E-Mail gefunden. Bitte überprüfen Sie Ihre E-Mail und versuchen Sie es erneut.</p>', isFound