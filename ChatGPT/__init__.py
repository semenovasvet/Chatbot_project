import openai
import logging
import requests
import os
from typing import *
from dotenv import load_dotenv

load_dotenv()


class OpenAiClass:
    def __init__(self, body) -> None:
        self.body = body

    def call_openAi(self, action: Literal = ["chat", "embeddings"]):
        try:
            if action == "chat":
                url = " https://api.openai.com/v1/chat/completions"
            elif action == "embeddings":
                url = "https://api.openai.com/v1/embeddings"

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"
            }

            # body = {
            #     "model": "gpt-3.5-turbo",
            #     "messages": [
            #         {
            #             "role": "system",
            #             "content": "You are a helpful assistant."
            #         },
            #         {
            #             "role": "user",
            #             "content": "Hello!"
            #         }
            #     ]
            # }

            response = requests.post(url=url, headers=headers, json=self.body)
            return response.text
        
        except KeyError:
            logging.warning(f"The key is wrong")

        except Exception as e:
            logging.warning(e)

