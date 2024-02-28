import logging
from enum import Enum
from typing import Optional, List
from sgqlc.operation import Operation
from ..graphql_query.query import Query
from .. import shopifyClasses
from . import Shopify_Operations
from .. import config


class QueryShopify(Shopify_Operations):
    def __init__(self) -> None:
        super().__init__()


    def query_shopify(self, entityName: str, **kwargs) -> Optional[dict]:
        schema = Operation(Query)
        query_method = getattr(schema, entityName)
        query_method(**kwargs)
        response = self.shopify_post(schema)
        if entityName in ["catalogs", "orders", "customers","companyLocations", "products", "productVariants"] and "nodes" in response[entityName]:
            return response[entityName]["nodes"]
        return response[entityName]
    

    def query_products(self, query: str, cursor: str) -> dict:
        schema = Operation(Query)
        products_iterator = schema.products_iterator(first=50, query=query, after=cursor)
        products_iterator.nodes.id()
    

    def query_companyLocations(self, query: str) -> Optional[List[shopifyClasses.CompanyLocation]]:
        schema = Operation(Query)
        companyLocations = schema.companyLocations(first=50, query=query)
        companyLocations.nodes.id()
        companyLocations.nodes.company()
        buyerExperienceConfiguration = companyLocations.nodes.buyerExperienceConfiguration()
        buyerExperienceConfiguration.checkoutToDraft()
        buyerExperienceConfiguration.editableShippingAddress()
        paymentTermsTemplate = buyerExperienceConfiguration.paymentTermsTemplate()
        response = self.shopify_post(schema)
        if response["companyLocations"]["nodes"] and len(response["companyLocations"]["nodes"]) < 50:
            return [shopifyClasses.CompanyLocation(**node) for node in response["companyLocations"]["nodes"]]
        return []
    

    def query_companyLocation(self, id: str) -> Optional[shopifyClasses.CompanyLocation]:
        schema = Operation(Query)
        companyLocation = schema.companyLocation(id=id)
        companyLocation.id()
        companyLocation.name()
        company = companyLocation.company()
        company.id()
        company.name()
        company.mainContact()
        contacts = company.contacts(first=10)
        contacts.nodes.id()
        contacts.nodes.isMainContact()
        contacts.nodes.createdAt()
        customer = contacts.nodes.customer()
        customer.id()
        customer.email()
        customer.tags()
        company.contactRoles(first=10)
        company.defaultRole()
        companyLocation.billingAddress()
        companyLocation.shippingAddress()
        roleAssignments = companyLocation.roleAssignments(first=10)
        roleAssignments.nodes.id()
        roleAssignments.nodes.companyContact()
        roleAssignments.nodes.role()
        response = self.shopify_post(schema)
        if "companyLocation" in response and response["companyLocation"]:
            return shopifyClasses.CompanyLocation(**response["companyLocation"])
        return None
    

    def query_company(self, id: str) -> Optional[shopifyClasses.Company]:
        schema = Operation(Query)
        company = schema.company(id=id)
        company.id()
        company.name()
        contactRoles = company.contactRoles(first=10)
        contactRoles.nodes.id()
        contactRoles.nodes.name()
        response = self.shopify_post(schema)
        if "company" in response and response["company"]:
            return shopifyClasses.Company(**response["company"])
        return None
    

    def query_customer(self, id: str) -> Optional[shopifyClasses.Customer]:
        schema = Operation(Query)
        customer = schema.customer(id=id)
        customer.id()
        customer.firstName()
        customer.lastName()
        customer.email()
        customer.acceptsMarketing()
        customer.phone()
        customer.createdAt()
        customer.updatedAt()
        customer.verifiedEmail()
        customer.validEmailAddress()
        customer.tags()
        customer.lifetimeDuration()
        customer.addresses()
        customer.companyContactProfiles()
        response = self.shopify_post(schema)
        if "customer" in response and response["customer"]:
            return shopifyClasses.Customer(**response["customer"])
        return None
    

    def query_catalog(self, id:str) -> Optional[shopifyClasses.Catalog]:
        schema = Operation(Query)
        catalog = schema.catalog(id=id)
        catalog.id()
        catalog.title()
        catalog.status()
        priceList = catalog.priceList()
        priceList.id()
        priceList.fixedPricesCount()
        priceList.name()
        priceList.parent()
        response = self.shopify_post(schema)
        if "catalog" in response and response["catalog"]:
            return shopifyClasses.Catalog(**response["catalog"])
        return None
    
    def query_orders(self, query: str) -> Optional[List[dict]]:
        schema = Operation(Query)
        orders = schema.orders(first=50, query=query)
        orders.nodes.id()
        orders.nodes.name()
        orders.nodes.email()
        orders.nodes.displayFinancialStatus()
        orders.nodes.fulfillments(first=50)
        response = self.shopify_post(schema)
        if response["orders"]["nodes"] and len(response["orders"]["nodes"]) < 50:
            return response["orders"]["nodes"]
        else:
            logging.warning("tooo many")
            return response["orders"]["nodes"]
        return None