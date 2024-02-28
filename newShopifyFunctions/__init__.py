import logging
from typing import Literal
from .shopify_operations.metafield import Metafield
from .shopify_operations.customer import Customer
from .shopify_operations.catalog import Catalog
from .shopify_operations.company import Company
from . import config
from .config import Metafield_Key, Payment_Terms, Email_Subscription, Catalog_Status, PriceList_Adjustment_Type, PriceList_CompareAtMode


class Shopify:
    def __init__(self) -> None:
        self.metafield = Metafield()
        self.customer = Customer()
        self.catalog = Catalog()
        self.company = Company()

    
    def metafield_update(self, owner_id: str, value: str, metafield_key: str) -> dict:
        """ update metafield in shopify -> {"success": bool, "errors": Optional[dict, list, str]}"""
        if not all([owner_id, value, metafield_key]):
            raise ValueError(f"Some of the values might be absent: {owner_id=}, {value=}, {metafield_key=}")
        if config.BASE_SHOPIFY_ID not in owner_id:
            raise ValueError(f'ownerId must be in format {config.BASE_SHOPIFY_ID}')
        if type(value) != str:
            raise TypeError("value must be of type str")
        if not any(member.value == metafield_key for member in Metafield_Key):
            raise ValueError(f'Resource should be one of: {[member.value for member in Metafield_Key]}')
        
        response = self.metafield.metafield_update(owner_id, value, metafield_key)
        action = config.METAFIELD_UPDATE
        if response and action in response and response[action] and response[action]["metafields"]:
            logging.info(f'Metafield {metafield_key} for {owner_id} was updated!')
            return {"success": True, "errors": response[action][config.USER_ERRORS]}
        logging.error(f'Error when trying to update metafield {metafield_key} for {owner_id}: {response}')
        return {"success": False, "errors": response}
    

    def metafield_delete(self, variantId: str, metafield_key: str = Metafield_Key.VARIANT_DISCOUNT_DELETE.value) -> dict:
        """ delete metafield in shopify -> {"success": bool, "errors": Optional[dict, list, str]}"""
        if not all([variantId, metafield_key]):
            raise ValueError(f"Some of the values might be absent: {variantId=}, {metafield_key=}")
        if config.SHOPIFY_ID_VARIANT not in variantId:
            raise ValueError(f'variantId must be in format {config.SHOPIFY_ID_VARIANT}')
        if not any(member.value == metafield_key for member in Metafield_Key):
            raise ValueError(f'key must be one of {[member.value for member in Metafield_Key]}')
        
        response = self.metafield.metafield_delete(variantId, metafield_key)
        action = config.METAFIELD_DELETE
        if response and action in response and response[action] and response[action]["deletedId"]:
            logging.info(f'Metafield was successfully deleted!')
            return {"success": True, "errors": response[action][config.USER_ERRORS]}
        elif response and "Metafield_is_empty" in response:
            return {"success": True, "errors": None}
        logging.error(f'Error when trying to delete metafield for {variantId}: {response}')
        return {"success": False, "errors": response}


    def customer_create(self, email: str,
                            address: str = "",
                            city: str = "",
                            zipcode: str = "",
                            countryCode: str = "",
                            firstName: str = "",
                            lastName: str = "",
                            phone: str = "",
                            company: str = "",
                            emailSubscription: str = Email_Subscription.NOT_SUBSCRIBED.value,
                            tags: list = []) -> dict:
        """create a customer in shopify -> {"success": bool, "id": str, "emailIsTaken": bool, "errors": Optional[dict, list, str]}"""
        if not all([email, emailSubscription]):
            raise ValueError(f"Some of the values might be absent: {email=}, {emailSubscription=}")
        if not any(member.value == emailSubscription for member in Email_Subscription):
            raise ValueError(f'emailSubscription must be one of {[member.value for member in Email_Subscription]}')
        
        action = config.CUSTOMER_CREATE
        response = self.customer.customer_create(email, address, city, zipcode, countryCode, firstName, lastName, phone, company, emailSubscription, tags)
        if response and action in response and response[action]:
            if response[action]["customer"]:
                logging.info(f'New customer with id {response[action]["customer"]["id"]} was created!')
                return {"success": True, "id": response[action]["customer"]["id"], "emailIsTaken": False, "errors": response[action][config.USER_ERRORS]}
            elif not response[action]["customer"] and response[action][config.USER_ERRORS] and response[action][config.USER_ERRORS][0]["message"] == "Email address has already been taken.":
                logging.error(f"E-Mail {email} is already taken!")
                return {"success": False, "id": None, "emailIsTaken": True, "errors": f'Error when trying to create a new company: {response[action][config.USER_ERRORS]}'}
        logging.error(f'Error when trying to create a new customer: {response}')
        return {"success": False, "id": None, "emailIsTaken": False, "errors": response}
    

    def customer_update(self, id: str, tags: list = []) -> dict:
        """update a customer in shopify -> {"success": bool, "errors": Optional[dict, list, str]}"""
        if not all([id]):
            raise ValueError(f"Some of the values might be absent: {id=}")
        if config.SHOPIFY_ID_CUSTOMER not in id:
            raise ValueError(f'id must be in format {config.SHOPIFY_ID_CUSTOMER}')
        
        action = config.CUSTOMER_UPDATE
        response = self.customer.customer_update(id, tags)
        if response and action in response and response[action]:
            logging.info(f'Customer with id {id} was updated!')
            return {"success": True, "errors": response[action][config.USER_ERRORS]}
        logging.error(f'Error when trying to update customer with id {id}: {response}')
        return {"success": False, "errors": response}
    

    def catalog_create(self, title: str, companyLocationId: str, catalogStatus: str = Catalog_Status.ACTIVE.value) -> dict:
        """create a customer in shopify -> {"success": bool, "id": str, "errors": Optional[dict, list, str]}"""

        if not all([title, companyLocationId, catalogStatus]):
            raise ValueError(f"Some of the values might be absent: {title=}, {companyLocationId=}, {catalogStatus=}")
        if config.SHOPIFY_ID_COMPANY_LOCATION not in companyLocationId:
            raise ValueError(f"companyLocationId must be in format {config.SHOPIFY_ID_COMPANY_LOCATION}")
        if not any(member.value == catalogStatus for member in Catalog_Status):
            raise ValueError(f'catalogStatus must be one of {[member.value for member in Catalog_Status]}')

        action = config.CATALOG_CREATE
        response = self.catalog.catalog_create(title, companyLocationId, catalogStatus)
        if response and action in response and response[action] and response[action]["catalog"]:
            logging.info(f"New catalog with the title {title} was created!")
            return {"success": True, "id": response[action]["catalog"]["id"], "errors": response[action][config.USER_ERRORS]}
        logging.error(f'Error when creating catalog: {response}')
        return {"success": False, "id": None, "errors": response}
    

    def priceList_create(self, catalogId: str,
                                adjustment_value: float = config.DEFAULT_ADJUSTMENT_VALUE,
                                adjustment_type: str = PriceList_Adjustment_Type.PERCENTAGE_DECREASE.value,
                                compareAtMode: str = PriceList_CompareAtMode.ADJUSTED.value,
                                currency: str = config.DEFAULT_CURRENCY) -> dict:
        """create a price list for the catalog"""

        if not all([catalogId, adjustment_type, compareAtMode, currency]) or adjustment_value is None:
            raise ValueError(f"Some of the values might be absent: {catalogId=}, {adjustment_value=}, {adjustment_type=}, {compareAtMode=}, {currency=}")
        if config.SHOPIFY_ID_CATALOG not in catalogId:
            raise ValueError(f'catalogId must be in format {config.SHOPIFY_ID_CATALOG}')
        if type(adjustment_value) != float:
            raise TypeError("adjustment_value must be of type float")
        if not any(member.value == adjustment_type for member in PriceList_Adjustment_Type):
            raise ValueError(f'adjustment_type must be one of {[member.value for member in PriceList_Adjustment_Type]}')
        if not any(member.value == compareAtMode for member in PriceList_CompareAtMode):
            raise ValueError(f'compareAtMode must be one of {[member.value for member in PriceList_CompareAtMode]}')
        
        action = config.PRICE_LIST_CREATE
        response = self.catalog.priceList_create(catalogId, adjustment_value, adjustment_type, compareAtMode, currency)
        if response and action in response and response[action] and response[action]["priceList"]:
            logging.info(f'New price list {response[action]["priceList"]["id"]} was created!')
            return {"success": True, "id": response[action]["priceList"]["id"], "errors": response[action][config.USER_ERRORS]}
        logging.error(f'Error when trying to create a new price list: {response}')
        return {"success": False, "id": None, "errors": f'Error when trying to create a new price list: {response}'}
    

    def priceList_delete(self, priceListId: str) -> dict:
        """delete priceList by id"""
        if not all([priceListId]):
            raise ValueError(f"Some of the values might be absent: {priceListId=}")
        if config.SHOPIFY_ID_PRICE_LIST not in priceListId:
            raise ValueError(f"priceListId must be in format {config.SHOPIFY_ID_PRICE_LIST}")
        
        action = config.PRICE_LIST_DELETE
        response = self.catalog.priceList_delete(priceListId)
        if response and action in response and response[action] and response[action]["deletedId"]:
            logging.info(f"Action {action} was successful")
            return {"success": True, "errors": response[action][config.USER_ERRORS]}
        logging.error(f'Error when trying to {action} for {priceListId}: {response}')
        return {"success": False, "errors": response}
    

    def priceList_addPrices(self, priceListId: str, pricesList: list) -> dict:
        """add fixed prices for products or productVariants"""
        if not all([priceListId, pricesList]):
            raise ValueError(f"Some of the values might be absent: {priceListId=}, {pricesList=}")
        if type(pricesList) != list:
            raise TypeError("pricesList must be of type list")
        if config.SHOPIFY_ID_PRICE_LIST not in priceListId:
            raise ValueError(f'priceListId must be in format {config.SHOPIFY_ID_PRICE_LIST}')

        action = config.PRICE_LIST_ADD
        response = self.catalog.priceList_addPrices(priceListId, pricesList)
        if response and action in response and response[action] and response[action]["prices"]:
            logging.info(f"Price list in {priceListId} was updated!")
            return {"success": True, "errors": response[action][config.USER_ERRORS]}
        logging.error(f'Error when trying to update price list {priceListId}: {response}')
        return {"success": False, "errors": f'Error when trying to update price list {priceListId}: {response}'}
    

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
                            paymentTermsTemplateId: str = Payment_Terms.TEMPLATE_15_DAYS.value) -> dict:
        """ create a company"""
        if not all([companyName, email, address, city, zipcode, countryCode, paymentTermsTemplateId]):
            raise ValueError(f"Some of the values might be absent: {companyName=}, {email=}, {address=}, {city=}, {zipcode=}, {countryCode=}, {paymentTermsTemplateId=}")
        if not any(member.value == paymentTermsTemplateId for member in Payment_Terms):
            raise ValueError(f'paymentTermsTemplateId must be one of {[member.value for member in Payment_Terms]}')

        action = config.COMPANY_CREATE
        response = self.company.company_create(companyName, email, address, city, zipcode, countryCode, phone, firstName, lastName, checkoutToDraft, editableShippingAddress, paymentTermsTemplateId)
        if response and action in response and response[action]:
            if response[action]["company"]:
                logging.info(f'New company with id {response[action]["company"]["id"]} was created!')
                return {"success": True, "id": response[action]["company"]["id"], "emailIsTaken": False, "errors": response[action][config.USER_ERRORS]}
            elif not response[action]["company"] and response[action][config.USER_ERRORS] and response[action][config.USER_ERRORS][0]["message"] == "Email address has already been taken.":
                logging.error(f"E-Mail {email} is already taken!")
                return {"success": False, "id": None, "emailIsTaken": True, "errors": f'Error when trying to create a new company: {response[action][config.USER_ERRORS]}'}
        logging.error(f'Error when trying to create a new company: {response}')
        return {"success": False, "id": None, "emailIsTaken": False, "errors": response}
    

    def company_addCustomer(self, companyId: str, customerId: str) -> dict:
        """add customer to the company"""

        if not all([companyId, customerId]):
            raise ValueError(f"Some of the values might be absent: {companyId=}, {customerId=}")
        if config.SHOPIFY_ID_COMPANY not in companyId:
            raise ValueError(f'companyId must be in format {config.SHOPIFY_ID_COMPANY}')
        if config.SHOPIFY_ID_CUSTOMER not in customerId:
            raise ValueError(f'customerId must be in format {config.SHOPIFY_ID_CUSTOMER}')
        
        action = config.COMPANY_ADD_CONTACT
        response = self.company.company_addCustomer(companyId, customerId)
        if response and action in response and response[action] and response[action]["companyContact"]:
            logging.info(f"Customer {customerId} was successfully added to company {companyId}")
            return {"success": True, "errors": response[action][config.USER_ERRORS]}
        logging.error(f'Error when trying to add customer {customerId} to company {companyId}: {response}')
        return {"success": False, "errors": response}


    def company_assignMainContact(self, companyContactId: str, companyId: str) -> dict:
        """assign company contact as the main contact of the company"""

        if not all([companyContactId, companyId]):
            raise ValueError(f"Some of the values might be absent: {companyContactId=}, {companyId=}")
        if config.SHOPIFY_ID_COMPANY_CONTACT not in companyContactId:
            raise ValueError(f'companyContactId must be in format {config.SHOPIFY_ID_COMPANY_CONTACT}')
        if config.SHOPIFY_ID_COMPANY not in companyId:
            raise ValueError(f'companyId must be in format {config.SHOPIFY_ID_COMPANY}')
        
        action = config.COMPANY_ASSIGN_MAIN_CONTACT
        response = self.company.company_assignMainContact(companyId=companyId, companyContactId=companyContactId)
        if response and action in response and response[action] and response[action]["company"]:
            logging.info(f'CompanyContact {companyContactId} was assigned as the main role to company {companyId}')
            return {"success": True, "errors": response[action][config.USER_ERRORS]}
        logging.error(f'Error when trying to assign companyContact {companyContactId} to company {companyId} as the main contact {response}')
        return {"success": False, "errors": response}
    

    def company_ContactDelete(self, companyContactId: str) -> dict:
        """delete company contact"""

        if not all([companyContactId]):
            raise ValueError(f"Some of the values might be absent: {companyContactId=}")
        if config.SHOPIFY_ID_COMPANY_CONTACT not in companyContactId:
            raise ValueError(f'companyContactId must be in format {config.SHOPIFY_ID_COMPANY_CONTACT}')
        
        action = config.COMPANY_CONTACT_DELETE
        response = self.company.company_deleteContact(companyContactId)
        if response and action in response and response[action] and response[action]["deletedCompanyContactId"]:
            logging.info(f'CompanyContact {companyContactId} was successfully deleted')
            return {"success": True, "errors": response[action][config.USER_ERRORS]}
        print(response)
        logging.error(f'Error when trying to delete companyContact {companyContactId} {response[action][config.USER_ERRORS]}')
        return {"success": False, "errors": response}
    

    def companyLocation_AssignRoles(self, companyLocationId: str, companyContactId: str, companyContactRoleId: str) -> dict:
        """Assign company contact a role in company location"""

        if not all([companyLocationId, companyContactId, companyContactRoleId]):
            raise ValueError(f"Some of the values might be absent: {companyLocationId=}, {companyContactId=}, {companyContactRoleId=}")
        if config.SHOPIFY_ID_COMPANY_LOCATION not in companyLocationId:
            raise ValueError(f'companyLocationId must be in format {config.SHOPIFY_ID_COMPANY_LOCATION}')
        if config.SHOPIFY_ID_COMPANY_CONTACT not in companyContactId:
            raise ValueError(f'companyContactId must be in format {config.SHOPIFY_ID_COMPANY_CONTACT}')
        if config.SHOPIFY_ID_COMPANY_CONTACT_ROLE not in companyContactRoleId:
            raise ValueError(f'companyContactRoleId must be in format {config.SHOPIFY_ID_COMPANY_CONTACT_ROLE}')
        
        
        action = config.COMPANY_LOCATION_ASSIGN_ROLES
        response = self.company.companyLocation_assignRoles(companyLocationId, companyContactId, companyContactRoleId)
        if response and action in response and response[action] and response[action]["roleAssignments"]:
            logging.info(f'CompanyContact {companyContactId} was successfully assigned as a role {companyContactRoleId} to companyLocation {companyLocationId}')
            return {"success": True, "errors": response[action][config.USER_ERRORS]}
        logging.error(f'Error when trying to assign companyContact {companyContactId} to companyLocation {companyLocationId} as role {companyContactRoleId}: {response}')
        return {"success": False, "errors": response}
    

    def companyLocation_RevokeRoles(self, companyLocationId: str, roleToRevoke: str) -> dict:
        """Revoke company contact role from company location"""

        if not all([companyLocationId, roleToRevoke]):
            raise ValueError(f"Some of the values might be absent: {companyLocationId=}, {roleToRevoke=}")
        if config.SHOPIFY_ID_COMPANY_LOCATION not in companyLocationId:
            raise ValueError(f'companyLocationId must be in format {config.SHOPIFY_ID_COMPANY_LOCATION}')
        if config.SHOPIFY_ID_COMPANY_CONTACT_ROLE_ASSIGNMENT not in roleToRevoke:
            raise ValueError(f'roleToRevoke must be in format {config.SHOPIFY_ID_COMPANY_CONTACT_ROLE_ASSIGNMENT}')
        
        action = config.COMPANY_LOCATION_REVOKE_ROLES
        response = self.company.companyLocation_revokeRoles(companyLocationId, roleToRevoke)
        if response and action in response and response[action] and response[action]["revokedRoleAssignmentIds"]:
            logging.info(f'CompanyRole {roleToRevoke} was successfully revoked from companyLocation {companyLocationId}')
            return {"success": True, "errors": response[action][config.USER_ERRORS]}
        logging.error(f'Error when trying to revoke companyRole {roleToRevoke} from companyLocation {companyLocationId}: {response}')
        return {"success": False, "errors": response}
    

    def companyLocation_update(self, companyLocationId: str, paymentTermsTemplate: Payment_Terms) -> dict:
        """update company location"""

        if not all([companyLocationId, paymentTermsTemplate]):
            raise ValueError(f"Some of the values might be absent: {companyLocationId=}, {paymentTermsTemplate=}")
        if config.SHOPIFY_ID_COMPANY_LOCATION not in companyLocationId:
            raise ValueError(f'companyLocationId must be in format {config.SHOPIFY_ID_COMPANY_LOCATION}')
        if not any(member.value == paymentTermsTemplate for member in Payment_Terms):
            raise ValueError(f'paymentTermsTemplate must be one of {[member.value for member in Payment_Terms]}')
        
        action = config.COMPANY_LOCATION_UPDATE
        response = self.company.companyLocation_update(companyLocationId, paymentTermsTemplate)
        if response and action in response and response[action] and response[action]["companyLocation"]:
            logging.info(f'CompanyLocation {companyLocationId} was successfully updated')
            return {"success": True, "errors": response[action][config.USER_ERRORS]}
        logging.error(f'Error when trying to update companyLocation {companyLocationId}: {response}')
        return {"success": False, "errors": response}