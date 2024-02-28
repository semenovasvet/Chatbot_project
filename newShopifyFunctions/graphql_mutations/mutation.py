from sgqlc.types import Type, Field, list_of, non_null, Input
from .catalog import CatalogCreatePayload, CatalogCreateInput, CompanyLocationIds, CatalogStatus
from .metafield import MetafieldsSetPayload, MetafieldDeletePayload, MetafieldsSetInput, MetafieldDeleteInput
from .customer import CustomerCreatePayload, CustomerCreateInput, CustomerEmailMarketingState, CustomerEmailMarketingConsentInput, AddressCustomer, CustomerUpdateInput
from .priceList import PriceListAddFixedPricesPayload, PriceListCreatePayload, PriceListCreateInput, PriceListDeletePayload, PriceListDeleteInput, PriceListAdjustmentType, CompareAtMode, PriceListAdjustmentInput, PriceListAdjustmentSettingsInput, PriceListParentCreateInput, Prices, Price, CompareAtPrice
from .company import CompanyCreatePayload, CompanyCreateInput, CompanyLocationInput, CompanyContactInput, CompanyInput, AddressInput, BuyerExperienceConfigurationInput, CompanyAssignCustomerAsContactPayload, CompanyAssignMainContactPayload, CompanyContactDeletePayload, CompanyLocationAssignRolesPayload, CompanyLocationRoleAssignInput, CompanyLocationRevokeRolesPayload, CompanyLocationUpdatePayload, CompanyLocationUpdateInput
from . import UserError, CurrencyCode, CountryCode


class Mutation(Type):
    metafieldsSet = Field(MetafieldsSetPayload, args={'metafields': non_null(MetafieldsSetInput)})
    metafieldDelete = Field(MetafieldDeletePayload, args={"input": non_null(MetafieldDeleteInput)})

    catalogCreate = Field(CatalogCreatePayload, args={"input": non_null(CatalogCreateInput)})

    customerCreate = Field(CustomerCreatePayload, args={"input": non_null(CustomerCreateInput)})
    customerUpdate = Field(CustomerCreatePayload, args={"input": non_null(CustomerUpdateInput)})
    
    priceListCreate = Field(PriceListCreatePayload, args={"input": non_null(PriceListCreateInput)})
    priceListDelete = Field(PriceListDeletePayload, args={"id": non_null(str)})
    priceListFixedPricesAdd = Field(PriceListAddFixedPricesPayload, args={"priceListId": non_null(str), "prices": list_of(Prices)})

    companyCreate = Field(CompanyCreatePayload, args={"input": non_null(CompanyCreateInput)})
    companyAssignCustomerAsContact = Field(CompanyAssignCustomerAsContactPayload, args={"companyId": non_null(str), "customerId": non_null(str)})
    companyAssignMainContact = Field(CompanyAssignMainContactPayload, args={"companyContactId": non_null(str), "companyId": non_null(str)})
    companyContactDelete = Field(CompanyContactDeletePayload, args={"companyContactId": non_null(str)})

    companyLocationAssignRoles = Field(CompanyLocationAssignRolesPayload, args={"companyLocationId": non_null(str), "rolesToAssign": (non_null(list_of(CompanyLocationRoleAssignInput)))})
    companyLocationRevokeRoles = Field(CompanyLocationRevokeRolesPayload, args={"companyLocationId": non_null(str), "rolesToRevoke": (non_null(list_of(str)))})
    companyLocationUpdate = Field(CompanyLocationUpdatePayload, args={"companyLocationId": non_null(str), "input": non_null(CompanyLocationUpdateInput)})