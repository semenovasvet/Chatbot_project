from typing import Generic, TypeVar
from sgqlc.types import Type, Field, list_of
from sgqlc.types.relay import Connection, connection_args
from .customer import Email, Company_CustomerVar, Customer, CustomerConnection



class PaymentTermsTemplate(Type):
   id = str
   name = str

class BuyerExperienceConfiguration(Type):
   checkoutToDraft = bool
   editableShippingAddress = bool
   paymentTermsTemplate = Field(PaymentTermsTemplate)


class CompanyAddress(Type):
   id = str
   address1 = str
   city = str
   countryCode = str
   recipient = str
   zip = str
   phone = str


class Customer_CompanyVar(Type):
   id = str
   email = str
   tags = list_of(str)


class CompanyContact_CompanyVar(Type):
   id = str
   isMainContact = bool
   company = Field(Company_CustomerVar)
   createdAt = str
   customer = Field(Customer_CompanyVar)


class CompanyContactConnection(Connection):
   nodes = list_of(CompanyContact_CompanyVar)


class CompanyContactRole(Type):
   id = str
   name = str


class ContactRoleConnection(Connection):
   nodes = list_of(CompanyContactRole)


class MainContact(Type):
   id = str
   isMainContact = bool


class Company(Type):
  id = str
  name = str
  mainContact = Field(MainContact)
  contactRoles = Field(ContactRoleConnection, args=connection_args())
  contacts = Field(CompanyContactConnection, args=connection_args())
  defaultRole = Field(CompanyContactRole)


class RoleAssignment(Type):
   id = str
   companyContact = Field(CompanyContact_CompanyVar)
   role = Field(CompanyContactRole)


class RoleAssignmentConnection(Connection):
   nodes = list_of(RoleAssignment)
   

class CompanyLocation(Type):
   id = str
   name = str
   company = Field(Company)
   billingAddress = Field(CompanyAddress)
   shippingAddress = Field(CompanyAddress)
   roleAssignments = Field(RoleAssignmentConnection, args=connection_args())
   buyerExperienceConfiguration = Field(BuyerExperienceConfiguration)


class CompanyLocationConnection(Connection):
    nodes = list_of(CompanyLocation)

