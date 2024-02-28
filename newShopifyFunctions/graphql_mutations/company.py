from sgqlc.types import Type, Field, list_of, non_null, Input, Enum
from ..graphql_query.company import Company, CompanyContact_CompanyVar, RoleAssignment
from . import UserError, CountryCode


class UpdatedCompanyLocation(Type):
    id = str


class CompanyLocationRoleAssignInput(Input):
    companyContactId = str
    companyContactRoleId = str


class AddressInput(Input):
    address1 = str
    city = str
    countryCode = CountryCode
    recipient = str
    zip = str
    phone = str


class BuyerExperienceConfigurationInput(Input):
    checkoutToDraft = bool
    editableShippingAddress = bool
    paymentTermsTemplateId = str


class CompanyLocationUpdateInput(Input):
    buyerExperienceConfiguration = BuyerExperienceConfigurationInput


class CompanyLocationInput(Input):
    billingAddress = Field(AddressInput)
    shippingAddress = Field(AddressInput)
    buyerExperienceConfiguration = Field(BuyerExperienceConfigurationInput)


class CompanyContactInput(Input):
    firstName = str
    lastName = str
    email = str
    phone = str


class CompanyInput(Input):
    name = str


class CompanyCreateInput(Input):
    company = Field(CompanyInput)
    companyContact = Field(CompanyContactInput)
    companyLocation = Field(CompanyLocationInput)


class CompanyCreatePayload(Type):
    company = list_of(Company)
    userErrors = list_of(UserError)


class CompanyAssignCustomerAsContactPayload(Type):
    companyContact = CompanyContact_CompanyVar
    userErrors = list_of(UserError)


class CompanyAssignMainContactPayload(Type):
    company = Company
    userErrors = list_of(UserError)


class CompanyContactDeletePayload(Type):
    deletedCompanyContactId = str
    userErrors = list_of(UserError)


class CompanyLocationAssignRolesPayload(Type):
    roleAssignments = list_of(RoleAssignment)
    userErrors = list_of(UserError)


class CompanyLocationRevokeRolesPayload(Type):
    revokedRoleAssignmentIds = list_of(str)
    userErrors = list_of(UserError)


class CompanyLocationUpdatePayload(Type):
    companyLocation = UpdatedCompanyLocation
    userErrors = list_of(UserError)