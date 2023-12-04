import requests, json, logging


class Shopify:
    def __init__(self, salesOrderNumber: str) -> None:
        self.salesOrderNumber = salesOrderNumber
        with open('templates\graphql.json', 'r') as file:
            file = file.read()
            self.templates = json.loads(file)
        self.headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": "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"
        }
    
    def main(self):
        salesOrderId = self.find_order(self.salesOrderNumber)
        if salesOrderId:
            trackingLink = self.get_tracking_link(salesOrderId)
            if trackingLink:
                return {"order": True, "shipment": True, "url": trackingLink}
            else:
                return {"order": True, "shipment": False, "url": None}
        else:
            logging.warning("order was not found")
            return {"order": False, "shipment": False, "url": None}

    
    def find_order(self, salesOrderNumber):
        endpoint = "graphql.json"
        url = f"https://d4cb5c.myshopify.com/admin/api/2023-10/{endpoint}"
        variables = {"myquery": f"name:{salesOrderNumber} AND updated_at:>2023-10-01"}
        query = self.templates["query"]
        body = {"query": query,
                "variables":  variables}
        response = requests.post(url=url, json=body, headers=self.headers)
        response = json.loads(response.text)
        if response and "data" in response and response["data"]["orders"]["edges"]:
            salesOrderId = response["data"]["orders"]["edges"][0]["node"]["id"]
            return salesOrderId
    
    def get_tracking_link(self, salesOrderId):
        endpoint = "graphql.json"
        url = f"https://d4cb5c.myshopify.com/admin/api/2023-10/{endpoint}"
        variables = {"id": salesOrderId}
        query = self.templates["order"]
        body = {"query": query,
                "variables":  variables}
        response = requests.post(url=url, json=body, headers=self.headers)
        response = json.loads(response.text)
        if response and "data" in response and response["data"]["order"]["fulfillments"]:
            print(response)
            tracking_link = response["data"]["order"]["fulfillments"][0]["trackingInfo"][0]["url"]
            return tracking_link