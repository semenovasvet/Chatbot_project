import logging
from typing import Literal
from sgqlc.operation import Operation
# from util.shopifyFunctions.graphql_mutations.mutation import Mutation, CurrencyCode, CountryCode, CompanyCreatePayload, CompanyCreateInput, CompanyLocationInput, CompanyContactInput, CompanyInput, AddressInput, BuyerExperienceConfigurationInput, CompanyLocationRoleAssignInput, CompanyLocationUpdateInput
from ..shopify_schema import Mutation, CurrencyCode, CountryCode, CompanyCreatePayload, CompanyCreateInput, CompanyLocationInput, CompanyContactInput, CompanyInput, CompanyAddressInput, BuyerExperienceConfigurationInput, CompanyLocationRoleAssign, CompanyLocationUpdateInput
from . import Shopify_Operations
from .. import config
from ..config import Payment_Terms


class Company(Shopify_Operations):
    def __init__(self) -> None:
        super().__init__()
    
    def company_create(self, companyName: str,
                            email: str,
                            address: str ,
                            city: str,
                            zipcode: str,
                            countryCode: str,
                            phone: str = None,
                            firstName: str = "",
                            lastName: str = "",
                            checkoutToDraft: bool = False,
                            editableShippingAddress: bool = True,
                            paymentTermsTemplateId: str = Payment_Terms.TEMPLATE_30_DAYS) -> dict:
        """create schema input, create schema with this input -> send to shopify"""

        company_input = CompanyCreateInput(
            company = CompanyInput(
                name = companyName
            ),
            company_contact = CompanyContactInput(
                email = email,
                first_name = firstName,
                last_name = lastName
            ),
            company_location = CompanyLocationInput(
                billing_address = CompanyAddressInput(
                    address1 = address,
                    city = city,
                    country_code = self.find_choice(CountryCode, countryCode),
                    recipient = f"{firstName} {lastName}",
                    zip = zipcode
                ),
                shipping_address = CompanyAddressInput(
                    address1 = address,
                    city = city,
                    country_code = self.find_choice(CountryCode, countryCode),
                    recipient = f"{firstName} {lastName}",
                    zip = zipcode
                ),
                buyer_experience_configuration = BuyerExperienceConfigurationInput(
                    checkout_to_draft = checkoutToDraft,
                    editable_shipping_address = editableShippingAddress,
                    payment_terms_template_id = paymentTermsTemplateId
                )
            )
        )
        if phone:
            company_input.company_contact.phone = phone
            company_input.company_location.billing_address.phone = phone
            company_input.company_location.shipping_address.phone = phone
        schema = Operation(Mutation)
        company_create = schema.company_create(input=company_input)
        company_create.company().id()
        company_create.user_errors()
        response = self.shopify_post(schema)
        return response


    def company_addCustomer(self, companyId: str, customerId: str) -> dict:
        """create schema input, create schema with this input -> send to shopify"""

        schema = Operation(Mutation)
        schema.company_assign_customer_as_contact(company_id=companyId, customer_id=customerId)
        response = self.shopify_post(schema)
        return response
    

    def company_assignMainContact(self, companyId: str, companyContactId: str) -> dict:
        """create schema input, create schema with this input -> send to shopify"""

        schema = Operation(Mutation)
        schema.company_assign_main_contact(company_id=companyId, company_contact_id=companyContactId)
        response = self.shopify_post(schema)
        return response
    

    def company_deleteContact(self, companyContactId: str) -> dict:
        """create schema input, create schema with this input -> send to shopify"""

        schema = Operation(Mutation)
        schema.company_contact_delete(company_contact_id=companyContactId)
        response = self.shopify_post(schema)
        return response
    

    def companyLocation_assignRoles(self, companyLocationId: str, companyContactId: str, companyContactRoleId: str) -> dict:
        """create schema input, create schema with this input -> send to shopify"""
        companyLocationRoleAssignInput = CompanyLocationRoleAssign(
            company_contact_id = companyContactId,
            company_contact_role_id = companyContactRoleId
        )
        schema = Operation(Mutation)
        schema.company_location_assign_roles(company_location_id=companyLocationId, roles_to_assign = [companyLocationRoleAssignInput])
        response = self.shopify_post(schema)
        return response


    def companyLocation_revokeRoles(self, companyLocationId: str, roleToRevoke: str) -> dict:
        """create schema input, create schema with this input -> send to shopify"""
   
        schema = Operation(Mutation)
        schema.company_location_revoke_roles(company_location_id=companyLocationId, roles_to_revoke = [roleToRevoke])
        response = self.shopify_post(schema)
        return response
    
    
    def companyLocation_update(self,  companyLocationId: str, paymentTermsTemplate: Payment_Terms) -> dict:
        """create schema input, create schema with this input -> send to shopify"""
        companyLocationInput = CompanyLocationUpdateInput(
            buyer_experience_configuration = BuyerExperienceConfigurationInput(
                payment_terms_template_id = paymentTermsTemplate
            )
        )
        schema = Operation(Mutation)
        company_location_update = schema.company_location_update(company_location_id=companyLocationId, input=companyLocationInput)
        company_location_update.company_location().id()
        company_location_update.user_errors()
        response = self.shopify_post(schema)
        return response