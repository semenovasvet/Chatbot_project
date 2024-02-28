import requests
import json
import logging
from typing import *
import os
from dotenv import load_dotenv
from . import config

load_dotenv()

class Shopify:
    def __init__(self) -> None:
        with open(config.PATH_TO_GRAPHQL_QUERIES, "r") as f:
            self.template = json.load(f)
        self.headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": os.environ["shopifyAccessToken"]
        }


    def rest_shopify(self, action: Literal["products", "product", "variant", "variants"], 
                   id: int = None, customQuery: str = None):
        """returns a list of products/variants OR a single product/variant"""

        if action not in ["products", "product", "variant", "variants"]:
            raise ValueError('Action should be one of: ["products", "product", "variant", "variants]')

        if action == "products":
            endpoint = "products.json"+customQuery if customQuery else "products.json"
        
        elif action == "variants":
            endpoint = "variants.json"+customQuery if customQuery else "variants.json"

        elif action == "product" and id is not None:
            endpoint = f"products/{id}.json"

        elif action == "variant" and id is not None:
            endpoint = f"variants/{id}.json"

        url = f"{config.SHOPIFY_URL}{endpoint}"

        response = requests.get(url=url, headers=self.headers)
        if response.ok and action in json.loads(response.text):
            return json.loads(response.text)[action]

    
    def change_metafield(self, id: int, resource: Literal["variants", "products"],
                         json_dict: dict):
        """change metafield in product or productVariant"""

        if resource not in ["variants", "products"]:
            raise ValueError('Resource should be one of: ["variants", "products"]')
        
        if resource == "products":
            key = config.PRODUCT_KEY
        elif resource == "variants":
            key = config.VARIANT_KEY # "sliderpricerules_variant"
        
        endpoint = f"{resource}/{id}/metafields.json"
        body = {
            "metafield": {
                "value": json.dumps(json_dict),
                "owner_id": id,
                "namespace": config.CUSTOM,
                "key": key,
                "owner_resource": resource,
                "type": config.JSON
            }
        }
        url = f"{config.SHOPIFY_URL}{endpoint}"
        response = requests.post(url=url, headers=self.headers, json=body)
        if response.ok:
            logging.warning(f"{key} metafield in Shopify is updated!")
        else:
            logging.error(f"Error while updating metafield: {response.content}")
        return response.status_code, response.content
    

    def delete_metafield(self, id: int, resource: Literal["variants", "products"]):
        """delete metafield in product or productVariant"""

        if resource not in ["variants", "products"]:
            raise ValueError('Resource should be one of: ["variants", "products"]')
        
        if resource == "products":
            key = config.PRODUCT_KEY
        elif resource == "variants":
            key = config.VARIANT_KEY # "sliderpricerules_variant"
        
        endpoint = f"{resource}/{id}/metafields.json?key={key}"
        
        url = f"{config.SHOPIFY_URL}{endpoint}"
        response = requests.get(url=url, headers=self.headers)
        if response.ok:
            metafields = json.loads(response.text)["metafields"]
            if len(metafields) == 1:
                metafieldId = metafields[0]["id"]
                newEndpoint = f"{resource}/{id}/metafields/{metafieldId}.json"
                url = f"{config.SHOPIFY_URL}{newEndpoint}"
                deleteResponse = requests.delete(url=url, headers=self.headers)
                if deleteResponse.ok:
                    logging.warning("Metafield was successfully deleted!")
            elif len(metafields) == 0:
                 logging.error(f"No completed metafield with key {key} was found for {resource} with id {id}")
            else:
                 logging.error(f"More than one metafield with key {key} was found for {resource} with id {id}")


    def graphql_shopify(self, action: str, variables: dict):
        """send data in graphQL -> response / None"""

        url = f"{config.SHOPIFY_URL}graphql.json"
        query = self.template[action]
        body = {
                "query": query,
                "variables": variables
            }
        
        response = requests.post(url=url, headers=self.headers, json=body)
        if "data" in json.loads(response.text):
            return json.loads(response.text)["data"]
        else:
            logging.error(f"Response code: {response.status_code}, content: {response.content}")
            return None
        

    def shopify_query(self, action:Literal["products_query", 
                                            "productVariants_query", 
                                            "automaticDiscountNodes_query",
                                            "customers_query",
                                            "catalogs_query",
                                            "orders_query",
                                            "companyLocations_query"], 
                            query: str):
        """send query to shopify -> [dict,...]"""

        if not query or not action:
            raise ValueError("query and action are required")
        if type(query) != str:
            raise TypeError('query: format must be "title:test rabatt 2" or "sku:"HM-9800015-5000""')
        variables = {"myquery": query}
        response = self.graphql_shopify(action, variables)
        if response:
            return response[action.strip("_query")]["edges"]
    

    def get_entity(self, action:Literal["customer_id", "catalog_id", "company_id", "order_id"], entityId:str):
        """get entity by id"""

        if action not in ["customer_id", "catalog_id", "company_id"]:
            raise ValueError('Action should be one of: ["customer_id", "catalog_id", "company_id"]')
        if not entityId:
            raise ValueError("entityId is required to find an entity")
        if "gid://shopify/" not in entityId:
            raise ValueError("entityId must be in format 'gid://shopify/Customer/7386507116868'")
        variables = {"id": f"{entityId}"}
        response = self.graphql_shopify(action, variables)
        if response:
            return response[action.strip("_id")]
        
    
    def delete_entity(self, action:Literal["priceListDelete"], entityId: str):
        """delete entity by id"""

        if action not in ["priceListDelete"]:
            raise ValueError('Action should be one of: ["priceListDelete"]')
        if not entityId:
            raise ValueError("entityId is required for delete action")
        if "gid://shopify/" not in entityId:
            raise ValueError("entityId must be in format 'gid://shopify/PriceList/30316036420")
        variables = {"id": entityId}
        response = self.graphql_shopify(action, variables)
        if response:
            if response[action] and not response[action]["deletedId"] and response[action][config.USER_ERRORS]:
                logging.error(f'Error when trying to {action} entity {entityId}: {response[action][config.USER_ERRORS]}')
                return False
            elif response[action] and response[action]["deletedId"]:
                logging.warning(f"Action {action} was successful")
                return True


    def create_catalog(self, title: str, companyLocationId: str, publicationId: str = None):
        """create catalog"""

        if not title or not companyLocationId:
            raise ValueError("title and companyLocationId are required for creating a catalog!")
        if "gid://shopify/CompanyLocation/" not in companyLocationId:
            raise ValueError("companyLocationId must in format 'gid://shopify/CompanyLocation/3131179332")
        if publicationId and "gid://shopify/Publication/" not in publicationId:
            raise ValueError('publicationId must be in format gid://shopify/Publication/178920653124')
        inputDict = {
                "context": {
                "companyLocationIds": [
                    companyLocationId
                ]
                },
                "status": config.ACTIVE_STATUS,
                "title": title
            }
        if publicationId:
            inputDict["publicationId"] = publicationId
        variables = {
            "input": inputDict
        }
        action = config.CATALOG_CREATE
        response = self.graphql_shopify(action, variables)
        if response and not response[action]["catalog"] and response[action][config.USER_ERRORS]:
            logging.error(f'Error when trying to create a new catalog: {response[action][config.USER_ERRORS]}')
            return None
        elif response and response[action]["catalog"]:
            logging.warning(f"New catalog with the title {title} was created!")
            return response[action]["catalog"]["id"]


    def create_company(self, companyName: str,
                            email: str,
                            address: str,
                            city: str,
                            zipcode: str,
                            countryCode: str,
                            phone: str = None,
                            firstName: str = "",
                            lastName: str = "",
                            checkoutToDraft: bool = False,
                            editableShippingAddress: bool = True):
        """ create a company"""

        if not all([companyName, email, address, city, zipcode, countryCode]):
            raise ValueError("companyName, email, address, city, zipcode, countryCode are required for creating a company")
        
        company_contact = {
        "email": email,
        "firstName": firstName,
        "lastName": lastName
        }

        company_location = {
            "billingAddress": {
                "address1": address,
                "city": city,
                "countryCode": countryCode,
                "recipient": f"{firstName} {lastName}",
                "zip": zipcode
            },
            "buyerExperienceConfiguration": {
                "checkoutToDraft": checkoutToDraft,
                "editableShippingAddress": editableShippingAddress
            },
            "shippingAddress": {
                "address1": address,
                "city": city,
                "countryCode": countryCode,
                "recipient": f"{firstName} {lastName}",
                "zip": zipcode
            }
        }
        if phone:
            company_contact["phone"] = phone
            company_location["billingAddress"]["phone"] = phone
            company_location["shippingAddress"]["phone"] = phone

        variables = {
            "input": {
                "company": {"name": companyName},
                "companyContact": company_contact,
                "companyLocation": company_location
            }
        }
        action = config.COMPANY_CREATE
        response = self.graphql_shopify(action, variables)
        if response and not response[action]["company"] and response[action][config.USER_ERRORS]:
            logging.error(f'Error when trying to create a new company: {response[action][config.USER_ERRORS]}')
            if response[action][config.USER_ERRORS][0]["message"] == "Email address has already been taken.":
                return None, True
            return None, False
        elif response and response[action]["company"]:
            logging.warning(f'New company with id {response[action]["company"]["id"]} was created!')
            return response[action]["company"]["id"], False
    

    def company_addCustomer(self, companyId: str, customerId: str):
        """add customer to the company"""

        if "gid://shopify/Company/" not in companyId:
            raise ValueError('companyId must be in format "gid://shopify/Company/2723512644"')
        if "gid://shopify/Customer/" not in customerId:
            raise ValueError('customerId must be in format "gid://shopify/Customer/7386507116868"')
        
        variables = {
            "companyId": companyId,
            "customerId": customerId
        }
        action = config.COMPANY_ADD_CONTACT
        response = self.graphql_shopify(action, variables)
        if response and not response[action]["companyContact"] and response[action][config.USER_ERRORS]:
            logging.error(f'Error when trying to add customer {customerId} to company {companyId}: {response[action][config.USER_ERRORS]}')
            return False
        elif response and response[action]["companyContact"]:
            logging.warning(f"Customer {customerId} was successfully aded to company {companyId}")
            return True
    

    def company_assignMainContact(self, companyContactId: str, companyId: str):
        """assign company contact as the main contact of the company"""

        if "gid://shopify/CompanyContact/" not in companyContactId:
            raise ValueError('catalogId must be in format "gid://shopify/CompanyContact/2887188804"')
        if "gid://shopify/Company/" not in companyId:
            raise ValueError('catalogId must be in format "gid://shopify/Company/2740322628"')
        
        variables = {
            "companyContactId": companyContactId,
            "companyId": companyId
        }
        action = config.COMPANY_ASSIGN_MAIN_CONTACT
        response = self.graphql_shopify(action, variables)
        if response and not response[action]["company"] and response[action][config.USER_ERRORS]:
            logging.error(f'Error when trying to assign companyContact {companyContactId} to company {companyId} as the main contact {response[action][config.USER_ERRORS]}')
            return False
        elif response and response[action]["company"]:
            logging.warning(f'CompanyContact {companyContactId} was assigned as the main role to company {companyId}')
            return True
        
    
    def company_ContactDelete(self, companyContactId):
        """delete company contact"""

        if "gid://shopify/CompanyContact/" not in companyContactId:
            raise ValueError('catalogId must be in format "gid://shopify/CompanyContact/2887188804"')
        
        variables = {
        "companyContactId": companyContactId
        }
        action = config.COMPANY_CONTACT_DELETE
        response = self.graphql_shopify(action, variables)
        if response and not response[action]["deletedCompanyContactId"] and response[action][config.USER_ERRORS]:
            logging.error(f'Error when trying to delete companyContact {companyContactId} {response[action][config.USER_ERRORS]}')
            return False
        elif response and response[action]["deletedCompanyContactId"]:
            logging.warning(f'CompanyContact {companyContactId} was successfully deleted')
            return True


    def create_priceList(self, catalogId: str,
                                adjustment_value: float = config.DEFAULT_ADJUSTMENT_VALUE,
                                adjustment_type: Literal["PERCENTAGE_DECREASE", "PERCENTAGE_INCREASE"] = config.DEFAULT_ADJUSTMENT_TYPE,
                                compareAtMode: Literal["ADJUSTED", "NULLIFY"] = config.DEFAULT_COMPARE_AT_MODE,
                                currency: str = config.DEFAULT_CURRENCY):
        """create a price list for the catalog"""

        if not catalogId:
            raise ValueError("catalogId is required for creating priceList")
        if "gid://shopify/CompanyLocationCatalog/" not in catalogId:
            raise ValueError('catalogId must be in format "gid://shopify/CompanyLocationCatalog/78917632324"')
        if type(adjustment_value) != float:
            raise TypeError("adjustment_value must be of type float")
        if adjustment_type not in ["PERCENTAGE_DECREASE", "PERCENTAGE_INCREASE"]:
            raise ValueError('adjustment_type must be one of "PERCENTAGE_DECREASE", "PERCENTAGE_INCREASE"')
        if compareAtMode not in ["ADJUSTED", "NULLIFY"]:
            raise ValueError('compareAtMode must be one of "ADJUSTED", "NULLIFY"')
        
        variables = {
            "input": {
                "catalogId": catalogId,
                "name": f"{catalogId} priceList",
                "currency": currency,
                "parent": {
                "adjustment": {
                    "type": adjustment_type,
                    "value": adjustment_value
                },
                "settings": {
                    "compareAtMode": compareAtMode
                }
                }
            }
        }
        action = config.PRICE_LIST_CREATE
        response = self.graphql_shopify(action, variables)
        if response and not response[action]["priceList"] and response[action][config.USER_ERRORS]:
            logging.warning(f'Error when trying to create a new price list: {response[action][config.USER_ERRORS]}')
            return None
        elif response and response[action]["priceList"]:
            logging.warning(f'New price list {response[action]["priceList"]["id"]} was created!')
            return response[action]["priceList"]["id"]
    

    def priceList_addPrices(self, priceListId: str,
                                pricesList: list, entity: Literal["variants", "products"]):
        """add fixed prices for products or productVariants"""

        if not priceListId or not pricesList:
            raise ValueError('priceListId and pricesList are required for adding prices')
        if "gid://shopify/PriceList/" not in priceListId:
            raise ValueError('priceListId must be in format "gid://shopify/PriceList/115567603"')
        if entity not in ["variants", "products"]:
            raise ValueError('Entity should be one of: ["variants", "products"]')
        
        if entity == "variants":
            action = config.PRICE_VARIANT_ACTION
            key = config.PRICE_VARIANT_KEY
            responseKey = config.PRICE_VARIANT_RESPONSE_KEY
        elif entity == "products":
            action = config.PRICE_PRODUCT_ACTION
            key = config.PRICE_PRODUCT_KEY
            responseKey = config.PRICE_PRODUCT_RESPONSE_KEY

        variables = {
            "priceListId": priceListId,
            key: pricesList
        }
        response = self.graphql_shopify(action, variables)
        if response and response[action][responseKey]:
            logging.warning(f"Price list for {entity} in {priceListId} was updated!")
    

    def create_customer(self, email: str,
                            address: str,
                            city: str,
                            zipcode: str,
                            countryCode: str,
                            firstName: str = "",
                            lastName: str = "",
                            phone: str = "",
                            company: str = "",
                            emailSubscription: Literal["NOT_SUBSCRIBED", "SUBSCRIBED", "UNSUBSCRIBED"] = "NOT_SUBSCRIBED"):
        """create a customer"""

        if not all([email, address, city, zipcode, countryCode]):
            raise ValueError("email,address, city, zipcode, countryCode are required for creating a customer")
        if emailSubscription not in ["NOT_SUBSCRIBED", "SUBSCRIBED", "UNSUBSCRIBED"]:
            raise ValueError('emailSubscription must be one of "NOT_SUBSCRIBED", "SUBSCRIBED", "UNSUBSCRIBED"')
        
        variables = {
            "input": {
                "email": email,
                "phone": phone,
                "firstName": firstName,
                "lastName": lastName,
                "emailMarketingConsent": {
                    "marketingState":emailSubscription
                },
                "addresses": [
                {
                    "address1": address,
                    "city": city,
                    "phone": phone,
                    "company": company,
                    "zip": zipcode,
                    "lastName": lastName,
                    "firstName": firstName,
                    "country": countryCode
                }
                ]
            }
        }
        action = config.CUSTOMER_CREATE
        response = self.graphql_shopify(action, variables)
        if response and not response[action]["customer"] and response[action][config.USER_ERRORS]:
            logging.warning(f'Error when trying to create a new customer: {response[action][config.USER_ERRORS]}')
            return None
        elif response and response[action]["customer"]:
            logging.warning(f'New customer {response[action]["customer"]["id"]} was created!')
            return response[action]["customer"]["id"]

########################################################################################################################################################

    # def create_publication(self, autoPublish: bool = False, defaultState: Literal["EMPTY", "ALL_PRODUCTS"] = "EMPTY"):
    #     variables = {
    #         "input": {
    #             "autoPublish": autoPublish,
    #             "defaultState": defaultState
    #         }
    #     }
    #     return self.graphql_shopify("publicationCreate", variables)


    # def update_publication(self, publicationId: str, list_to_add: list = [], list_to_remove:list = [], autoPublish: bool = False):
    #     if "gid://shopify/Publication/" not in publicationId:
    #         raise ValueError(f'publicationId must be in format "gid://shopify/Publication/178920653124"')
    #     variables = {
    #         "id": publicationId,
    #         "input": {
    #             "autoPublish": autoPublish,
    #             "publishablesToAdd": list_to_add,
    #             "publishablesToRemove": list_to_remove
    #         }
    #     }
    #     return self.graphql_shopify("publicationUpdate", variables)


    # def create_discount(self, title: str, 
    #                     percentage: float, 
    #                     quantity: str, 
    #                     product_variant_id: str, 
    #                     orderDiscounts: bool = True,
    #                     productDiscounts: bool = True,
    #                     shippingDiscounts: bool = True):
    #     if not all([title, percentage, quantity, product_variant_id]):
    #         raise ValueError("title, percentage, quantity and productId - are required for creating a discount")
    #     if type(percentage) != float:
    #         raise TypeError('percentage: value must be between 0.00 - 1.00')
    #     variables = {
    #             "automaticBasicDiscount": {
    #                 "title": title,
    #                 "startsAt": "2023-11-08T00:00:00Z",
    #                 "combinesWith": {
    #                     "orderDiscounts": orderDiscounts,
    #                     "productDiscounts": productDiscounts,
    #                     "shippingDiscounts": shippingDiscounts
    #                 },
    #                 "minimumRequirement": {
    #                 "quantity": {
    #                     "greaterThanOrEqualToQuantity": quantity
    #                 }
    #                 },
    #                 "customerGets": {
    #                 "value": {
    #                     "percentage": percentage
    #                 },
    #                 "items": {
    #                     "all": False,
    #                     "products": {
    #                         "productVariantsToAdd": [
    #                             f"gid://shopify/ProductVariant/{product_variant_id}"
    #                         ]
    #                     }
    #                 }
    #                 }
    #             }
    #         }
    #     return self.graphql_shopify("discountAutomaticBasicCreate", variables)
    

    # def update_discount(self, discountId: int,
    #                     percentage: float,
    #                     quantity: str):
    #     if not all([discountId, percentage, quantity]):
    #         raise ValueError("discountId, percentage and quantity - are required for updating a discount")
    #     if type(percentage) != float:
    #         raise TypeError('percentage: value must be between 0.00 - 1.00')
    #     variables = {
    #             "id": f"gid://shopify/DiscountAutomaticNode/{discountId}",
    #             "automaticBasicDiscount": {
    #                 "customerGets": {
    #                 "value": {
    #                     "percentage": percentage
    #                 }
                    
    #                 },
    #                 "minimumRequirement": {
    #                     "quantity": {
    #                         "greaterThanOrEqualToQuantity": quantity
    #                     }
    #                 }
    #             }
    #         }
    #     return self.graphql_shopify("discountAutomaticBasicUpdate", variables)


    # def delete_discount(self, discountId: int):
    #     if not discountId:
    #         raise ValueError("discountId is required for deleting a discount")
    #     variables = {
    #             "ids": [
    #                 f"gid://shopify/DiscountAutomaticNode/{discountId}"
    #             ]
    #         }
    #     return self.graphql_shopify("discountAutomaticBulkDelete", variables)