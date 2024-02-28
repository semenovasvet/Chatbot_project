from enum import Enum

PATH_TO_GRAPHQL_QUERIES = "util/shopifyFunctions/graphql_queries.json"
SHOPIFY_URL = "https://d4cb5c.myshopify.com/admin/api/2023-10/"

DEFAULT_CURRENCY = "EUR"
USER_ERRORS = "userErrors"


# actions
CATALOG_CREATE = "catalogCreate"
COMPANY_CREATE =  "companyCreate"
COMPANY_ADD_CONTACT = "companyAssignCustomerAsContact"
COMPANY_ASSIGN_MAIN_CONTACT = "companyAssignMainContact"
COMPANY_CONTACT_DELETE = "companyContactDelete"
COMPANY_LOCATION_ASSIGN_ROLES = "companyLocationAssignRoles"
COMPANY_LOCATION_REVOKE_ROLES = "companyLocationRevokeRoles"
COMPANY_LOCATION_UPDATE = "companyLocationUpdate"
CUSTOMER_CREATE = "customerCreate"
CUSTOMER_UPDATE = "customerUpdate"
METAFIELD_UPDATE = "metafieldsSet"
METAFIELD_DELETE = "metafieldDelete"
PRICE_LIST_CREATE = "priceListCreate"
PRICE_LIST_DELETE = "priceListDelete"


# shopify ids
BASE_SHOPIFY_ID = "gid://shopify/"
SHOPIFY_ID_PRODUCT = "gid://shopify/Product/"
SHOPIFY_ID_VARIANT = "gid://shopify/ProductVariant/"
SHOPIFY_ID_PRICE_LIST = "gid://shopify/PriceList/"
SHOPIFY_ID_COMPANY = "gid://shopify/Company/"
SHOPIFY_ID_COMPANY_LOCATION = "gid://shopify/CompanyLocation/"
SHOPIFY_ID_COMPANY_CONTACT = "gid://shopify/CompanyContact/"
SHOPIFY_ID_COMPANY_CONTACT_ROLE = "gid://shopify/CompanyContactRole/"
SHOPIFY_ID_COMPANY_CONTACT_ROLE_ASSIGNMENT = "gid://shopify/CompanyContactRoleAssignment/"
SHOPIFY_ID_CUSTOMER = "gid://shopify/Customer/"
SHOPIFY_ID_CATALOG = "gid://shopify/CompanyLocationCatalog/"


# metafield
class Metafield_Key(Enum):
    PRODUCT_DISCOUNT = "discount"
    VARIANT_DISCOUNT = "discount_variant"
    VARIANT_DISCOUNT_DELETE = "custom.discount_variant"
    ORDER_LIST_VARIANTS = "bestell_liste_variante_"
    ORDER_LIST_VARIANTS_2 = "bestell_liste_variante_2"
    ORDER_LIST_PRODUCTS = "bestell_liste_produkte_"

NAMESPACE_CUSTOM =  "custom"
TYPE_JSON = "json"
TYPE_LIST_VARIANTS = "list.variant_reference"


# catalog
class Catalog_Status(Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    DRAFT = "DRAFT"


# price list
class PriceList_Adjustment_Type(Enum):
    PERCENTAGE_INCREASE = "PERCENTAGE_INCREASE"
    PERCENTAGE_DECREASE = "PERCENTAGE_DECREASE"

class PriceList_CompareAtMode(Enum):
    ADJUSTED = "ADJUSTED"
    NULLIFY = "NULLIFY"

DEFAULT_ADJUSTMENT_VALUE = 0.0
PRICE_LIST_ADD = "priceListFixedPricesAdd"
PRICE_VARIANT_KEY = "prices"
PRICE_VARIANT_RESPONSE_KEY = "prices"

PRICE_PRODUCT_ACTION = "priceListFixedPricesByProductUpdate"
PRICE_PRODUCT_KEY = "pricesToAdd"
PRICE_PRODUCT_RESPONSE_KEY =  "pricesToAddProducts"


# payment terms templates
class Payment_Terms(Enum):
    TEMPLATE_7_DAYS = "gid://shopify/PaymentTermsTemplate/2"
    TEMPLATE_15_DAYS = "gid://shopify/PaymentTermsTemplate/3"
    TEMPLATE_30_DAYS = "gid://shopify/PaymentTermsTemplate/4"
    TEMPLATE_45_DAYS = "gid://shopify/PaymentTermsTemplate/8"
    TEMPLATE_60_DAYS = "gid://shopify/PaymentTermsTemplate/5"
    TEMPLATE_90_DAYS = "gid://shopify/PaymentTermsTemplate/6"
    TEMPLATE_ON_FULLFILLMENT = "gid://shopify/PaymentTermsTemplate/9"


# customer
class Email_Subscription(Enum):
    NOT_SUBSCRIBED = "NOT_SUBSCRIBED"
    SUBSCRIBED = "SUBSCRIBED"
    UNSUBSCRIBED = "UNSUBSCRIBED"


