"""HubSpot tools."""
from __future__ import annotations
import json
import hubspot
from hubspot.crm.contacts import ApiException, SimplePublicObjectInput
from hubspot.crm.deals import ApiException as DealsApiException
from hubspot.crm.companies import ApiException as CompaniesApiException
from langchain_core.tools import BaseTool
from pydantic.v1 import BaseModel, Field
from typing import Type, List
from src.auth.hubspot_auth import get_hubspot_access_token
from tabulate import tabulate

# --- Input Schemas ---
class GetContactsInput(BaseModel):
    pass

class CreateContactInput(BaseModel):
    properties: dict = Field(description="The properties of the new contact.")

class GetCompaniesInput(BaseModel):
    pass

class CreateCompanyInput(BaseModel):
    properties: dict = Field(description="The properties of the new company.")

class UpdateCompanyInput(BaseModel):
    company_id: str = Field(description="The ID of the company to update.")
    properties: dict = Field(description="The properties to update.")

class CreateDealInput(BaseModel):
    properties: dict = Field(description="The properties of the new deal.")

class UpdateDealInput(BaseModel):
    deal_id: str = Field(description="The ID of the deal to update.")
    properties: dict = Field(description="The properties to update.")

class GetDealPerformanceInput(BaseModel):
    pass

class GetContactsTableInput(BaseModel):
    pass

# --- Tool Implementations ---

class HubSpotLangchainTool(BaseTool):
    """A base tool for interacting with the HubSpot API."""
    name: str = "hubspot_base_tool"
    description: str = "A base tool for HubSpot operations."
    client: hubspot.Client = None

    def __init__(self, **data):
        super().__init__(**data)
        try:
            access_token = get_hubspot_access_token()
            self.client = hubspot.Client.create(access_token=access_token)
        except Exception as e:
            raise Exception(f"Failed to initialize HubSpot client: {e}")

    def _run(self, *args, **kwargs):
        raise NotImplementedError("This base tool should not be run directly.")

class GetContactsTool(HubSpotLangchainTool):
    name: str = "get_hubspot_contacts"
    description: str = "Retrieves and returns a list of contacts from HubSpot."
    args_schema: Type[BaseModel] = GetContactsInput

    def _run(self) -> str:
        try:
            all_contacts = []
            after = None
            while True:
                page = self.client.crm.contacts.basic_api.get_page(limit=100, after=after, properties=["firstname", "lastname", "email", "phone", "company"])
                all_contacts.extend([c.to_dict() for c in page.results])
                if not page.paging or not page.paging.next:
                    break
                after = page.paging.next.after
            return json.dumps(all_contacts, indent=4)
        except ApiException as e:
            return f"Error getting contacts from HubSpot: {e}"

class GetContactsTableTool(HubSpotLangchainTool):
    name: str = "get_hubspot_contacts_table"
    description: str = "Retrieves and returns a list of contacts from HubSpot in a formatted table."
    args_schema: Type[BaseModel] = GetContactsTableInput

    def _run(self) -> str:
        try:
            all_contacts = []
            after = None
            while True:
                page = self.client.crm.contacts.basic_api.get_page(limit=100, after=after, properties=["firstname", "lastname", "email", "phone", "company"])
                all_contacts.extend([c.to_dict() for c in page.results])
                if not page.paging or not page.paging.next:
                    break
                after = page.paging.next.after
            
            headers = ["ID", "First Name", "Last Name", "Email", "Phone", "Company"]
            rows = []
            for contact in all_contacts:
                props = contact.get('properties', {})
                rows.append([
                    contact.get('id'),
                    props.get('firstname'),
                    props.get('lastname'),
                    props.get('email'),
                    props.get('phone'),
                    props.get('company')
                ])
            return tabulate(rows, headers=headers, tablefmt="grid")
        except ApiException as e:
            return f"Error getting contacts from HubSpot: {e}"

class CreateContactTool(HubSpotLangchainTool):
    name: str = "create_hubspot_contact"
    description: str = "Creates a new contact in HubSpot."
    args_schema: Type[BaseModel] = CreateContactInput

    def _run(self, properties: dict) -> str:
        try:
            simple_public_object_input = SimplePublicObjectInput(properties=properties)
            api_response = self.client.crm.contacts.basic_api.create(
                simple_public_object_input=simple_public_object_input
            )
            return json.dumps(api_response.to_dict(), indent=4)
        except ApiException as e:
            return f"Error creating contact in HubSpot: {e}"

class GetCompaniesTool(HubSpotLangchainTool):
    name: str = "get_hubspot_companies"
    description: str = "Retrieves and returns a list of companies from HubSpot."
    args_schema: Type[BaseModel] = GetCompaniesInput

    def _run(self) -> str:
        try:
            all_companies = []
            after = None
            while True:
                page = self.client.crm.companies.basic_api.get_page(limit=100, after=after, properties=["name", "domain", "city", "industry"])
                all_companies.extend([c.to_dict() for c in page.results])
                if not page.paging or not page.paging.next:
                    break
                after = page.paging.next.after
            return json.dumps(all_companies, indent=4)
        except CompaniesApiException as e:
            return f"Error getting companies from HubSpot: {e}"

class CreateCompanyTool(HubSpotLangchainTool):
    name: str = "create_hubspot_company"
    description: str = "Creates a new company in HubSpot."
    args_schema: Type[BaseModel] = CreateCompanyInput

    def _run(self, properties: dict) -> str:
        try:
            simple_public_object_input = SimplePublicObjectInput(properties=properties)
            api_response = self.client.crm.companies.basic_api.create(
                simple_public_object_input=simple_public_object_input
            )
            return json.dumps(api_response.to_dict(), indent=4)
        except CompaniesApiException as e:
            return f"Error creating company in HubSpot: {e}"

class UpdateCompanyTool(HubSpotLangchainTool):
    name: str = "update_hubspot_company"
    description: str = "Updates an existing company in HubSpot."
    args_schema: Type[BaseModel] = UpdateCompanyInput

    def _run(self, company_id: str, properties: dict) -> str:
        try:
            simple_public_object_input = SimplePublicObjectInput(properties=properties)
            api_response = self.client.crm.companies.basic_api.update(
                company_id=company_id,
                simple_public_object_input=simple_public_object_input
            )
            return json.dumps(api_response.to_dict(), indent=4)
        except CompaniesApiException as e:
            return f"Error updating company in HubSpot: {e}"

class CreateDealTool(HubSpotLangchainTool):
    name: str = "create_hubspot_deal"
    description: str = "Creates a new deal in HubSpot."
    args_schema: Type[BaseModel] = CreateDealInput

    def _run(self, properties: dict) -> str:
        try:
            simple_public_object_input = SimplePublicObjectInput(properties=properties)
            api_response = self.client.crm.deals.basic_api.create(
                simple_public_object_input=simple_public_object_input
            )
            return json.dumps(api_response.to_dict(), indent=4)
        except DealsApiException as e:
            return f"Error creating deal in HubSpot: {e}"

class UpdateDealTool(HubSpotLangchainTool):
    name: str = "update_hubspot_deal"
    description: str = "Updates an existing deal in HubSpot."
    args_schema: Type[BaseModel] = UpdateDealInput

    def _run(self, deal_id: str, properties: dict) -> str:
        try:
            simple_public_object_input = SimplePublicObjectInput(properties=properties)
            api_response = self.client.crm.deals.basic_api.update(
                deal_id=deal_id,
                simple_public_object_input=simple_public_object_input
            )
            return json.dumps(api_response.to_dict(), indent=4)
        except DealsApiException as e:
            return f"Error updating deal in HubSpot: {e}"

class GetDealPerformanceTool(HubSpotLangchainTool):
    name: str = "get_hubspot_deal_performance"
    description: str = "Retrieves and returns deal performance data from HubSpot."
    args_schema: Type[BaseModel] = GetDealPerformanceInput

    def _run(self) -> str:
        try:
            all_deals = []
            after = None
            while True:
                page = self.client.crm.deals.basic_api.get_page(limit=100, after=after, properties=["dealname", "dealstage", "amount", "closedate"])
                all_deals.extend([d.to_dict() for d in page.results])
                if not page.paging or not page.paging.next:
                    break
                after = page.paging.next.after
            return json.dumps(all_deals, indent=4)
        except DealsApiException as e:
            return f"Error getting deal performance from HubSpot: {e}"