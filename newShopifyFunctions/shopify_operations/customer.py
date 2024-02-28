import logging
from enum import Enum
from typing import Literal
from sgqlc.operation import Operation
from ..graphql_mutations.mutation import Mutation, CustomerCreateInput, CustomerEmailMarketingState, CustomerEmailMarketingConsentInput, CountryCode, AddressCustomer, CustomerUpdateInput
from . import Shopify_Operations
from .. import config


class Customer(Shopify_Operations):
    def __init__(self) -> None:
        super().__init__()

    def customer_create(self, email: str,
                            address: str = "",
                            city: str = "",
                            zipcode: str = "",
                            countryCode: str = "",
                            firstName: str = "",
                            lastName: str = "",
                            phone: str = "",
                            company: str = "",
                            emailSubscription: Literal["NOT_SUBSCRIBED", "SUBSCRIBED", "UNSUBSCRIBED"] = "NOT_SUBSCRIBED",
                            tags: list = []) -> dict:
        """create schema input, create schema with this input -> send to shopify"""

        customer_input = CustomerCreateInput(
            email = email
        )
        if emailSubscription:
            customer_input.emailMarketingConsent = CustomerEmailMarketingConsentInput(marketingState = self.find_choice(CustomerEmailMarketingState, emailSubscription))
        customer_input.addresses = [AddressCustomer(address1 = address,
                                                    country = self.find_choice(CountryCode, countryCode),
                                                    firstName = firstName,
                                                    lastName = lastName,
                                                    phone = phone,
                                                    zip = zipcode,
                                                    city = city,
                                                    company = company)]
        if firstName:
            customer_input.firstName = firstName
        if lastName:
            customer_input.lastName = lastName
        if tags:
            customer_input.tags = tags

        schema = Operation(Mutation)
        schema.customerCreate(input=customer_input)
        response = self.shopify_post(schema)
        return response
    
    
    def customer_update(self, id: str, tags: list = []) -> dict:
        """create schema input, create schema with this input -> send to shopify"""

        customer_input = CustomerUpdateInput(
            id = id,
            tags = tags
        )

        schema = Operation(Mutation)
        schema.customerUpdate(input=customer_input)
        response = self.shopify_post(schema)
        return response