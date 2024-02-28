from sgqlc.types import Type, Field, list_of
from sgqlc.types.relay import Connection, connection_args


class Email(Type):
   email: str

class MainContactCustomer(Type):
   customer = Field(Email)

class Address(Type):
   firstName = str
   lastName = str
   address1 = str
   city = str
   country = str
   zip = str

class Company_CustomerVar(Type):
   id = str
   contactCount = int
   mainContact = Field(MainContactCustomer)

class CompanyContact(Type):
   id = str
   isMainContact = bool
   company = Field(Company_CustomerVar)
   createdAt = str
   customer = Field(Email)

class Customer(Type):
  id = str
  firstName = str
  lastName = str
  acceptsMarketing = bool
  email = str
  phone = str
  createdAt = str
  updatedAt = str
  verifiedEmail = bool
  validEmailAddress = bool
  tags = list_of(str)
  lifetimeDuration = str
  addresses = list_of(Address)
  companyContactProfiles = list_of(CompanyContact)


class CustomerConnection(Connection):
    nodes = list_of(Customer)
