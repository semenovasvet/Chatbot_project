from sgqlc.types import Type, Field, list_of, non_null, Input, Enum
from ..graphql_query.customer import Customer
from . import UserError


class CustomerCreatePayload(Type):
    customer = list_of(Customer)
    userErrors = list_of(UserError)


class CustomerEmailMarketingState(Enum):
    __choices__ = ('NOT_SUBSCRIBED', 'SUBSCRIBED', 'UNSUBSCRIBED', 'INVALID', 'PENDING', 'REDACTED')


class CustomerEmailMarketingConsentInput(Input):
    marketingState = CustomerEmailMarketingState


class AddressCustomer(Input):
    address1 = str
    address2 = str
    city = str
    company = str
    country = str
    firstName = str
    lastName = str
    phone = str
    zip = str


class CustomerCreateInput(Input):
    email = str
    firstName = str
    lastName = str
    addresses = list_of(AddressCustomer)
    emailMarketingConsent = CustomerEmailMarketingConsentInput
    tags = list_of(str)


class CustomerUpdateInput(Input):
    id = str
    tags = list_of(str)