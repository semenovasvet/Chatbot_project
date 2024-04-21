from django.shortcuts import render
from django.http import JsonResponse, HttpRequest, HttpResponse
import openai
import logging
import os
from dotenv import load_dotenv
from typing import Optional, Tuple, Union
import pandas as pd
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from shopifyFunctions.trackingUrl import ShopifyTracking
from . import config


load_dotenv()

class ChatBot:
    """  Core class for handling the operations of a chatbot.

    This class serves as the central processing unit of the chatbot application. 
    It is responsible for receiving messages from users, processing these
    messages to generate appropriate responses, and sending these responses back to the user interface.

    """
    def __init__(self) -> None:
        """
        Here the necessary components for the chatbot are set up. The class attributes are defined; 
        openai module is initialised using the API Key.

        Attributes:
            self.df (DataFrame): The previously created dataset of products is initialised as a pandas dataframe.
            productsDict (dict): A dictionary to store the information about the recommended products. Initially empty.
            completion_tokens (int): Counter for the number of output tokens generated from the openAI API. Set to 0.
            prompt_tokens (int): Counter for the number of input tokens used in prompts sent to openAI API. Set to 0.
        """
        self.df = pd.read_csv(config.DATASET_PATH)
        openai.api_key = os.environ['OPENAI_API_KEY']
        self.productsDict = {}
        self.completion_tokens = 0
        self.prompt_tokens = 0


    def main(self, request: HttpRequest) -> Union[JsonResponse, HttpResponse]:
        """
        Handles all incoming requests to the chatbot and routes them based on the request type and content.

        Parameters:
            request (HttpRequest): The HttpRequest object containing metadata and user data.

        Returns:
            JsonResponse/HttpResponse: Depending on the type of request, it returns:
                - JsonResponse: For POST requests, with relevant data such as messages, responses, and status flags.
                - HttpResponse: For GET requests, which renders the chatbot's user interface.

        The function distinguishes between different POST requests by checking the 'name' attribute in the POST data, which indicates the specific action required:
            - "productDescription": Generates a list of recommended products using embeddings.
            - "advice": Uses the open AI text generation API for generating chatbot's responses.
            - "salesOrderNumber": Searches for sales orders by number and returns a tracking link if found.
            - "email": Looks up existing sales orders by customer email and returns a tracking link(s) if found.
        """
        if request.method == "POST":
            if request.POST.get("name")=="productDescription":
                message = request.POST.get("message")
                response = self.find_embedding(message)
                return JsonResponse({"message": message, "response": response})
        
            elif request.POST.get("name")=="advice":
                message = request.POST.get("message")
                response, isEnd = self.ask_gpt(message)
                return JsonResponse({"message": message, "response": response, "isEnd": isEnd})

            elif request.POST.get("name")=="salesOrderNumber":
                message = request.POST.get("message")
                response, isFound = self.find_salesOrder(message)
                return JsonResponse({"message": message, "response": response, "isFound": isFound})

            elif request.POST.get("name")=="email":
                message = request.POST.get("message")
                response, isFound = self.find_customer(message)
                return JsonResponse({"message": message, "response": response, "isFound": isFound})
        
        elif request.method == "GET":
            return render(request, 'chatbot.html')


    def ask_gpt(self, message: str) -> Tuple[str, bool]:
        """
        Processes a user's message through the OpenAI Chat Completion API using predefined model settings,
        and provides a response formatted in HTML. The method uses a context setup to guide the AI's responses,
        referring to a product information dictionary for content accuracy. If the user's message signifies
        the end of the conversation, token counts are displayed.

        Parameters:
            message (str): The user's message to be processed by the AI model.

        Returns:
            Tuple (str, bool): A tuple containing:
                - An HTML formatted string of the AI's response.
                - A Boolean indicating if the conversation is considered ended based on the user's message.

        In the very end of the conversation returns the final message, 
        containing the total number of output and input tokens used during conversation.
        """
        # initializes openai module
        try:
            response = openai.ChatCompletion.create(
                model = config.LANGUAGE_MODEL,
                temperature = config.TEMPERATURE,
                messages=[
                    {"role": "system", "content": f"Du bist ein hilfreicher Assistent auf der Website altruan.com. Gib kurze Antworten. Nutze die Informationen aus diesem Dictionary, um die Fragen der Nutzer zu den Produkten zu beantworten: {self.productsDict}. Wenn die Frage des Benutzers über die im Dictionary gefundenen Informationen hinausgeht, antworte, dass die Frage nicht in dein Fachgebiet fällt."},
                    {"role": "user", "content": message},
                ]
            )
            if response:
                answer = response["choices"][0]["message"]["content"]
                # check whether user's message is the end of the conversation
                isEnd = self.is_end(message)
                self.completion_tokens += int(response["usage"]["completion_tokens"])
                self.prompt_tokens += int(response["usage"]["prompt_tokens"])

                if isEnd == "True":
                    return f'<p>{answer} <br>Completion_tokens: {self.completion_tokens}.<br>Prompt_tokens: {self.prompt_tokens}</p>', True
                
                else:
                    return f'<p>{answer}</p>', False
                
        except Exception as e:
            logging.error(f"An error occured when generating a reponse from chat gpt: {e}")
            return "<p> Could not process the message</p>", False
        

    def is_end(self, message: str) -> bool:
        """
        Determines if a given message from the user indicates the end of a conversation.
        
        Sends the message to the OpenAI API, which returns a string that needs
        interpretation to determine if it signifies the end of the conversation. The API is set to
        provide a boolean-like string based on the conversation context.

        Parameters:
            message (str): The message to analyze.

        Returns:
            bool: True if the message indicates the end of the conversation, False otherwise.
        """
        try:
            response = openai.ChatCompletion.create(
                model = config.IS_END_DEFAULT_MODEL,
                temperature = config.IS_END_DEFAULT_TEMPERATURE,
                messages=[
                    {"role": "system", "content": config.IS_END_DEFAULT_CONTEXT},
                    {"role": "user", "content": message},
                ]
            )
            if response:
                isEnd = response["choices"][0]["message"]["content"].strip().lower()
                self.completion_tokens += int(response["usage"]["completion_tokens"])
                self.prompt_tokens += int(response["usage"]["prompt_tokens"])
                return isEnd == "true"
        except Exception as e:
            logging.error(f"An error occurred when determining if the conversation should end: {e}")
            return False


    def find_embedding(self, query: str) -> str:
        """ Processes a user query to find and list the top five relevant products.

        Transforms the user's query into an embedding, searches a product collection for the top five
        matching products based on this embedding, identifies the cheapest product among them, and
        formats this information into an HTML string suitable for display on a web page.

        The results are saved into the self.productsDict dictionary. Each product's information includes
        ID, title, body content, type, price, and a URL endpoint.

        Parameters:
            query (str): The user's query string to be embedded.

        Returns:
            str: An HTML formatted string listing the top five products and highlighting the cheapest one.
        """
        try:
            # initialising the chroma client and finding the previously created collection of embeddings
            chroma_client = chromadb.PersistentClient()
            embedding_function = OpenAIEmbeddingFunction(api_key=os.environ.get('OPENAI_API_KEY'), model_name=config.EMBEDDING_MODEL)
            products_collection = chroma_client.get_or_create_collection(name='products_collection', embedding_function=embedding_function )
            
            # query the found collection using the user's query string
            results = products_collection.query(query_texts=query, n_results=config.NUMBER_OF_RECOMMENDED_PRODUCTS, include=['distances'])
            # extract the ids of the products - these ids are correspoding with the positions of products in the products database
            ids_list = [int(i) for i in results['ids'][0]]
            # find the id of the cheapest product
            minId = self.find_the_cheapest(ids_list)
            # transforms the data into HTML formatted string
            titles = []
            for id in ids_list:
                self.productsDict[id] = {"id": self.df["id"][id],
                                        "title": self.df["title"][id], 
                                        "body": self.df["body"][id], 
                                        "type": self.df["type"][id], 
                                        "price": self.df["price"][id], 
                                        "endpoint": self.df["endpoint"][id]}
                titles.append(f'<p><a href=https://altruan.com/products/{self.df["endpoint"][id]} target="blank">{self.df["title"][id]}</a> - von {self.df["price"][id]} €</p>')
            response = '<br>'.join(titles)
            # add information about the cheapest product
            cheapestProduct = f'<p>Das billigste dieser Produkte ist <a href=https://altruan.com/products/{self.df["endpoint"][minId]} target="blank">{self.df["title"][minId]}</a></p>'
            return "<p> Hier sind die Produkte, die am besten zu Ihrer Anfrage passen: <br>" + response + "<br>" + cheapestProduct + "</p"
        
        except Exception as e:
            logging.error(f"An error occurred when finding embedding: {str(e)}")
            return f"<p>An error occurred when finding embedding: {str(e)}</p>"


    def find_the_cheapest(self, ids_list: list) -> Optional[int]:
        """
        Finds the cheapest product from the list of recommended product IDs.

        Parameters:
            ids_list (list): A list of product IDs to search through. 
            Each ID represents the position of the product in the "productData.csv" dataframe.

        Returns:
            Optional[int]: The ID of the cheapest product, or None if no valid price comparison can be made.
        """
        if not ids_list:
            return None

        minPrice = float('inf')
        minId = None
        for num in ids_list:
            try:
                price = float(self.df.loc[num, "price"])
                if price < minPrice:
                    minPrice = price
                    minId = num
            except (KeyError, ValueError, TypeError):
                continue  # skip invalid IDs or non-numeric prices

        return minId



    def find_salesOrder(self, salesOrderNumber: str) -> Tuple[str, bool]:
        """
        Calls find_by_number function to find a sales order by its number ->
        returns the received results as an HTML response suitable for displaying to the user.

        Parameters:
            salesOrderNumber (str): The unique identifier for the sales order.

        Returns:
            tuple (str, bool): A tuple containing:
            - An HTML formatted string message.
            - A Boolean indicating if the order was found or not.
        """
        responseDict = ShopifyTracking().find_by_number(salesOrderNumber=salesOrderNumber)

        if not responseDict:
            raise ValueError(f"Error occured when executing 'find_by_number' function. No dictionary was returned.")
        
        if not responseDict["order"]:
            return  f'<p>Es wurde kein Kundenauftrag mit der Nummer {salesOrderNumber} gefunden. Bitte überprüfen Sie die Auftragsnummer und versuchen Sie es erneut.</p><button id="forgot-button" type="button" class="forgot-button" onclick="forgotNumber()" style="display:block">Ich habe die Auftragsnummer vergessen</button>', False
        
        else:
            if not responseDict["urls"]:
                return  f'<p>Ihre Bestellung wurde noch nicht versandt</p>', True
            
            else:
                if len(responseDict["urls"]) == 1:
                    return f'<p>Verwenden Sie diesen Link, um Ihre Bestellung zu verfolgen: <a href={responseDict["urls"][0]} target="blank">Auftrag {salesOrderNumber}</a></p>', True
                
                else:
                    linkString = ""
                    for url in responseDict["urls"]:
                        linkString += f'<a href={url} target="blank">Auftrag {salesOrderNumber}</a><br>'
                    return f'<p>Verwenden Sie diese Links, um Ihre Bestellung zu verfolgen:<br>{linkString}</p>', True


    def find_customer(self, email: str) -> Tuple[str, bool]:
        """
        Calls the find_by_email function to retrieve all sales orders associated with the given email address 
        from the past 90 days. It then formats the results into an HTML response suitable for user display.

        Parameters:
            email (str): The email address of the customer for whom to lookup orders.

        Returns:
            tuple (str, bool): A tuple containing:
                - An HTML formatted string message with details of the orders, if any.
                - A Boolean indicating whether any sales orders were found within the last 90 days.
        """
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