from pydantic import BaseModel
from typing import *
import logging
from . import Shopify




def createDataClassTemplate(newClassName:str, entity:dict, itemsName):
    # helps to generate Neu classes
    print(f"class {newClassName}(BaseModel, Blueprint):")
    for key, value in entity.items():
        if key == itemsName:
            classNameItemName = f"{itemsName[:1].upper()}{itemsName[1:]}"
            print(f"\t{key}: List[{classNameItemName}] = []")
        elif key == "customAttributes":
            print(f"\t{key}: List[WeclappMetaData] = []")
        else:
            print(f"\t{key}: {type(value).__name__}")
    print()
    print( f"\t# AutomationData")
    print( f'\tITEMS_NAME: str = "{itemsName}"')
    print( f"\tUSED_KEYS: set = set()")




class Blueprint:
    '''Dies Ist eine Klase, die nicht eigenständig vverwendet werden sollte'''
    def queryItems(self, key:str, value:Any, justParentItems:bool=True, raiseError:bool = True):
        try:
            for el in getattr(self, self.ITEMS_NAME):
                if getattr(el, key) == value:
                    if justParentItems:
                        if not hasattr(self, 'parentItemId'):
                            return el
                        else:
                            raise KeyError(f"Attribute is not ParentArticle -> it is not recomendet to edit this articles; else set justParentItems=False")
                        
                    else:
                        return el
            raise KeyError(f"Item {value} not found")

        except KeyError as e:
            if raiseError:
                raise e
            else:
                return None
    
    
            
    def setValue(self, key, value):
        assert hasattr(self, key), f"{type(self).__name__} has no attribute {key} -> check spelling, make sure it is included"
        setattr(self, key, value)
        self.USED_KEYS.add(key)
        
            
    def getUpdateDict(self, updateType:Literal['full', 'used']='full'):
        data = {}
        for key, value in self.__dict__.items():
            if value:
                try:
                    # handle contract Items
                    if key == self.ITEMS_NAME and hasattr(self, 'getUpdateDict'):
                        helper = []
                        for el in value:
                            h = el.getUpdateDict(updateType=updateType)
                            if updateType == 'full':
                                helper.append(h)
                            elif h:
                                helper.append(h)
                        if len(helper) > 0:
                            data[key] = helper

                    
                    # handl custom Attributes
                    elif key == "customAttributes":
                        helper = []
                        for el in value:
                            h = el.getUpdateDict(updateType=updateType)
                            if updateType == 'full':
                                helper.append(h)
                            elif h:
                                helper.append(h)
                        if len(helper) > 0:
                            data[key] = helper
                    
                    # Normal attributes
                    elif key in self.USED_KEYS or updateType == 'full':
                        if value != None:
                            data[key] = value  
                except Exception as e:
                    logging.error(f'Error at key {key=}')
                    raise e
        if data.get('ITEMS_NAME', False):
            del data["ITEMS_NAME"]
        if data.get('USED_KEYS', False):
            del data["USED_KEYS"]
        return data

    @classmethod
    def fromShopify(cls, id, action):
        response = Shopify().rest_shopify(action=action, id=id)
        return cls(**response)
    
    @classmethod
    def fromShopifyGQL(cls, action:Literal["customer_id", "catalog_id"], entityId):
        response = Shopify().get_entity(action=action, entityId=entityId)
        return cls(**response)
    # @classmethod
    # def fromDict(cls, entity:dict):
        
    #     return cls(**entity)
    
    @classmethod
    def blank(cls):
        fields = {field: None for field in cls.__fields__}
        return cls(**fields)


#############################################################################################################################################################################

class Address(BaseModel, Blueprint):
	id: Optional[str] = None
	address1: Optional[str] = None
	city: Optional[str] = None
	countryCode: Optional[str] = None
	recipient: Optional[str] = None
	zip: Optional[str] = None
	phone: Optional[str] = None

	# AutomationData
	ITEMS_NAME: str = ""
	USED_KEYS: set = set()

#############################################################################################################################################################################
class Variant(BaseModel, Blueprint):
	id: int
	product_id: int
	title: str
	price: str
	sku: str
	position: int
	inventory_policy: str
	compare_at_price: Optional[str] = None
	fulfillment_service: str
	inventory_management: Optional[str] = None
	option1: str
	option2: Optional[str] = None
	option3: Optional[str] = None
	created_at: str
	updated_at: str
	taxable: bool
	barcode: Optional[str]
	grams: int
	image_id: Optional[int] = None
	weight: float
	weight_unit: str
	inventory_item_id: int
	inventory_quantity: int
	old_inventory_quantity: int
	requires_shipping: bool
	admin_graphql_api_id: str

	# AutomationData
	ITEMS_NAME: str = ""
	USED_KEYS: set = set()


#############################################################################################################################################################################
class Product(BaseModel, Blueprint):
	id: int
	title: str
	body_html: str
	vendor: str
	product_type: str
	created_at: str
	handle: str
	updated_at: str
	published_at: Optional[str] = None
	template_suffix: Optional[str] = None
	published_scope: str
	tags: str
	status: str
	admin_graphql_api_id: str
	variants: Optional[List[Variant]] = []
	options: Optional[list] = []
	images: Optional[list] = []
	image: Optional[dict] = {}

	# AutomationData
	ITEMS_NAME: str = "variants"
	USED_KEYS: set = set()

#############################################################################################################################################################################


class PriceList(BaseModel, Blueprint):
	id: str
	fixedPricesCount: Optional[int] = None
	name: Optional[str] = None
	parent: Optional[dict] = {}

	# AutomationData
	ITEMS_NAME: str = "-"
	USED_ATTRIBUTES: dict = dict()
      

#############################################################################################################################################################################
class Catalog(BaseModel, Blueprint):
	id: str
	title: Optional[str] = None
	status: Optional[str] = None
	priceList: Optional[PriceList] = {}
	publication: Optional[dict] = {}

	# AutomationData
	ITEMS_NAME: str = "-"
	USED_ATTRIBUTES: dict = dict()


#############################################################################################################################################################################
     
class CompanyContact(BaseModel, Blueprint):
	id: str
	isMainContact: Optional[bool] = None
	company: Optional[dict] = {}
	createdAt: Optional[str] = None
	customer: Optional[dict] = {}

	# AutomationData
	ITEMS_NAME: str = "-"
	USED_ATTRIBUTES: dict = dict()


class CompanyContactConnection(BaseModel, Blueprint):
	nodes: List[CompanyContact] = []


#############################################################################################################################################################################
class Company(BaseModel, Blueprint):
	id: str
	name: Optional[str] = None
	mainContact: Optional[dict] = {}
	contacts: Optional[CompanyContactConnection] = {}
	contactRoles: Optional[dict] = {}
	defaultRole: Optional[dict] = {}

	# AutomationData
	ITEMS_NAME: str = ""
	USED_KEYS: set = set()



#############################################################################################################################################################################
class CompanyContactProfiles(BaseModel, Blueprint):
	company: Optional[Company] = {}
	createdAt: Optional[str] = None
	customer: Optional[dict] = {}
	id: str
	isMainContact: Optional[bool] = None

	# AutomationData
	ITEMS_NAME: str = "-"
	USED_ATTRIBUTES: dict = dict()
    

#############################################################################################################################################################################

class Customer(BaseModel, Blueprint):
	id: str
	firstName: Optional[str] = None
	lastName: Optional[str] = None
	acceptsMarketing: Optional[bool] = None
	email: Optional[str] = None
	phone: Optional[str] = None
	createdAt: Optional[str] = None
	updatedAt: Optional[str] = None
	companyContactProfiles: Optional[List[CompanyContactProfiles]] = []
	note: Optional[str] = None
	verifiedEmail: Optional[bool] = None
	validEmailAddress: Optional[bool] = None
	tags:  Optional[list] = []
	lifetimeDuration: Optional[str] = None
	defaultAddress:  Optional[dict] = {}
	addresses:  Optional[list] = []
	canDelete: Optional[bool] = None

	# AutomationData
	ITEMS_NAME: str = "-"
	USED_ATTRIBUTES: dict = dict()


#############################################################################################################################################################################
     
class RoleAssignment(BaseModel, Blueprint):
	id: str
	companyContact: Optional[CompanyContactProfiles] = {}
	role: Optional[dict] = {}

	# AutomationData
	ITEMS_NAME: str = ""
	USED_KEYS: set = set()


class RoleAssignmentNodes(BaseModel, Blueprint):
     nodes: List[RoleAssignment] = []

#############################################################################################################################################################################


class BuyerExperienceConfiguration(BaseModel, Blueprint):
	checkoutToDraft: Optional[bool] = None
	editableShippingAddress: Optional[bool] = None
	paymentTermsTemplate: Optional[dict] = {}

	# AutomationData
	ITEMS_NAME: str = ""
	USED_KEYS: set = set()
     

class CompanyLocation(BaseModel, Blueprint):
	id: str
	name: Optional[str] = None
	company: Optional[Company] = {}
	billingAddress: Optional[Address] = {}
	shippingAddress: Optional[Address] = {}
	roleAssignments: Optional[RoleAssignmentNodes] = {}
	buyerExperienceConfiguration: Optional[BuyerExperienceConfiguration] = {}

	# AutomationData
	ITEMS_NAME: str = ""
	USED_KEYS: set = set()