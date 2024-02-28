import logging
from typing import Literal
from sgqlc.operation import Operation
from ..graphql_mutations.mutation import Mutation, CurrencyCode, CountryCode, CompanyCreatePayload, CompanyCreateInput, CompanyLocationInput, CompanyContactInput, CompanyInput, AddressInput, BuyerExperienceConfigurationInput, CompanyLocationRoleAssignInput, CompanyLocationUpdateInput
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
            companyContact = CompanyContactInput(
                email = email,
                firstName = firstName,
                lastName = lastName
            ),
            companyLocation = CompanyLocationInput(
                billingAddress = AddressInput(
                    address1 = address,
                    city = city,
                    countryCode = self.find_choice(CountryCode, countryCode),
                    recipient = f"{firstName} {lastName}",
                    zip = zipcode
                ),
                shippingAddress = AddressInput(
                    address1 = address,
                    city = city,
                    countryCode = self.find_choice(CountryCode, countryCode),
                    recipient = f"{firstName} {lastName}",
                    zip = zipcode
                ),
                buyerExperienceConfiguration = BuyerExperienceConfigurationInput(
                    checkoutToDraft = checkoutToDraft,
                    editableShippingAddress = editableShippingAddress,
                    paymentTermsTemplateId = paymentTermsTemplateId
                )
            )
        )
        if phone:
            company_input.companyContact.phone = phone
            company_input.companyLocation.billingAddress.phone = phone
            company_input.companyLocation.shippingAddress.phone = phone
        schema = Operation(Mutation)
        schema.companyCreate(input=company_input)
        response = self.shopify_post(schema)
        return response


    def company_addCustomer(self, companyId: str, customerId: str) -> dict:
        """create schema input, create schema with this input -> send to shopify"""

        schema = Operation(Mutation)
        schema.companyAssignCustomerAsContact(companyId=companyId, customerId=customerId)
        response = self.shopify_post(schema)
        return response
    

    def company_assignMainContact(self, companyId: str, companyContactId: str) -> dict:
        """create schema input, create schema with this input -> send to shopify"""

        schema = Operation(Mutation)
        schema.companyAssignMainContact(companyId=companyId, companyContactId=companyContactId)
        response = self.shopify_post(schema)
        return response
    

    def company_deleteContact(self, companyContactId: str) -> dict:
        """create schema input, create schema with this input -> send to shopify"""

        schema = Operation(Mutation)
        schema.companyContactDelete(companyContactId=companyContactId)
        response = self.shopify_post(schema)
        return response
    

    def companyLocation_assignRoles(self, companyLocationId: str, companyContactId: str, companyContactRoleId: str) -> dict:
        """create schema input, create schema with this input -> send to shopify"""
        companyLocationRoleAssignInput = CompanyLocationRoleAssignInput(
            companyContactId = companyContactId,
            companyContactRoleId = companyContactRoleId
        )
        schema = Operation(Mutation)
        schema.companyLocationAssignRoles(companyLocationId=companyLocationId, rolesToAssign = [companyLocationRoleAssignInput])
        response = self.shopify_post(schema)
        return response


    def companyLocation_revokeRoles(self, companyLocationId: str, roleToRevoke: str) -> dict:
        """create schema input, create schema with this input -> send to shopify"""
   
        schema = Operation(Mutation)
        schema.companyLocationRevokeRoles(companyLocationId=companyLocationId, rolesToRevoke = [roleToRevoke])
        response = self.shopify_post(schema)
        return response
    
    
    def companyLocation_update(self,  companyLocationId: str, paymentTermsTemplate: Payment_Terms) -> dict:
        """create schema input, create schema with this input -> send to shopify"""
        companyLocationInput = CompanyLocationUpdateInput(
            buyerExperienceConfiguration = BuyerExperienceConfigurationInput(
                paymentTermsTemplateId = paymentTermsTemplate
            )
        )
        schema = Operation(Mutation)
        schema.companyLocationUpdate(companyLocationId=companyLocationId, input=companyLocationInput)
        response = self.shopify_post(schema)
        return response