import logging
from enum import Enum
from typing import Literal
from sgqlc.operation import Operation
from ..shopify_schema import Mutation, CustomerInput, CustomerEmailMarketingState, CustomerEmailMarketingConsentInput, CountryCode, MailingAddressInput, CustomerMarketingOptInLevel, CustomerEmailMarketingConsentUpdateInput
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
                            marketingOptInLevel: Literal["SINGLE_OPT_IN", "CONFIRMED_OPT_IN", "UNKNOWN"] = "SINGLE_OPT_IN",
                            tags: list = []) -> dict:
        """create schema input, create schema with this input -> send to shopify"""

        customer_input = CustomerInput(
            email = email
        )
        if emailSubscription:
            customer_input.email_marketing_consent = CustomerEmailMarketingConsentInput(marketing_state = self.find_choice(CustomerEmailMarketingState, emailSubscription), marketing_opt_in_level = self.find_choice(CustomerMarketingOptInLevel, marketingOptInLevel))
        addresses = MailingAddressInput()
        if address:
            addresses.address1 = address
        if city:
            addresses.city = city
        if zipcode:
            addresses.zip = zipcode
        if countryCode:
            addresses.country_code = self.find_choice(CountryCode, countryCode)
        if phone:
            addresses.phone = phone
        if company:
            addresses.company = company
        if tags:
            customer_input.tags = tags

        if firstName:
            addresses.first_name = firstName
            customer_input.first_name = firstName
        if lastName:
            addresses.last_name = lastName
            customer_input.last_name = lastName

        customer_input.addresses = [addresses]

        schema = Operation(Mutation)
        schema.customer_create(input=customer_input)
        response = self.shopify_post(schema)
        return response
    
    
    def customer_update(self, id: str, tags: list = []) -> dict:
        """create schema input, create schema with this input -> send to shopify"""

        customer_input = CustomerInput(
            id = id,
            tags = tags
        )

        schema = Operation(Mutation)
        schema.customer_update(input=customer_input)
        response = self.shopify_post(schema)
        return response
    

    def customer_marketing_consent_update(self, customerId: str, marketingOptInLevel:  Literal["SINGLE_OPT_IN", "CONFIRMED_OPT_IN", "UNKNOWN"] = "NOT_SUBSCRIBED", emailSubscription:  Literal["NOT_SUBSCRIBED", "SUBSCRIBED", "UNSUBSCRIBED"] = "NOT_SUBSCRIBED") -> dict:
        """create schema input, create schema with this input -> send to shopify"""
        emailConsent_input = CustomerEmailMarketingConsentUpdateInput(customer_id = customerId, 
                                                        email_marketing_consent = CustomerEmailMarketingConsentInput(
                                                            marketing_opt_in_level=self.find_choice(CustomerMarketingOptInLevel, marketingOptInLevel),
                                                            marketing_state=self.find_choice(CustomerEmailMarketingState, emailSubscription)))
        schema = Operation(Mutation)
        schema.customer_email_marketing_consent_update(input = emailConsent_input)
        response = self.shopify_post(schema)
        return response