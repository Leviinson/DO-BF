"""ZohoSDKAPI operations."""
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Iterator, List, Optional, Union

import httpx
from asgiref.sync import sync_to_async
from django.conf import settings
from zcrmsdk.src.com.zoho.crm.api import HeaderMap, Initializer, ParameterMap
from zcrmsdk.src.com.zoho.crm.api.file import FileOperations, GetFileParam
from zcrmsdk.src.com.zoho.crm.api.record import (
    ActionWrapper,
    APIException,
    BodyWrapper,
    DeleteRecordParam,
    GetRecordParam,
    GetRecordsParam,
)
from zcrmsdk.src.com.zoho.crm.api.record import Record as ZCRMRecord
from zcrmsdk.src.com.zoho.crm.api.record import (
    RecordOperations,
    ResponseWrapper,
    SearchRecordsParam,
    SuccessResponse,
)
from zcrmsdk.src.com.zoho.crm.api.record.file_body_wrapper import FileBodyWrapper
from zcrmsdk.src.com.zoho.crm.api.users import User
from zcrmsdk.src.com.zoho.crm.api.util import (
    APIHTTPConnector,
    APIResponse,
    StreamWrapper,
)

from config.constants import Constants


class CustomRecord:
    """Class for ZohoCRM customer record operations."""

    @staticmethod
    def get_user_id(response: APIResponse) -> Optional[int]:
        """Get successful response user 'customer zoho id'."""
        if response:
            response_object: object = response.get_object()
            if response_object:
                if isinstance(response_object, ActionWrapper):
                    action_response_list: list = response_object.get_data()
                    for action_response in action_response_list:
                        if isinstance(action_response, SuccessResponse):
                            details: dict = action_response.get_details()
                            return int(details.get("id"))

    @staticmethod
    def display_response(response: APIResponse) -> None:
        """Print response info."""
        if response is not None:
            print(f"Status Code: {response.get_status_code()}")

            if response.get_status_code() in [204, 304]:
                print("No Content" if response.get_status_code() == 204 else "Not Modified")
                return

            response_object: object = response.get_object()

            if response_object is not None:
                if isinstance(response_object, ActionWrapper):
                    action_response_list: list = response_object.get_data()

                    for action_response in action_response_list:
                        if isinstance(action_response, SuccessResponse):
                            print("Status: " + action_response.get_status().get_value())

                            print("Code: " + action_response.get_code().get_value())

                            print("Details")

                            details: dict = action_response.get_details()

                            for key, value in details.items():
                                print(key + " : " + str(value))

                            print("Message: " + action_response.get_message().get_value())

                        elif isinstance(action_response, APIException):
                            print("Status: " + action_response.get_status().get_value())

                            print("Code: " + action_response.get_code().get_value())

                            print("Details")

                            details: dict = action_response.get_details()

                            for key, value in details.items():
                                print(key + " : " + str(value))

                            print("Message: " + action_response.get_message().get_value())

                elif isinstance(response_object, APIException):
                    print("Status: " + response_object.get_status().get_value())

                    print("Code: " + response_object.get_code().get_value())

                    print("Details")

                    details: dict = response_object.get_details()

                    for key, value in details.items():
                        print(key + " : " + str(value))

                    print("Message: " + response_object.get_message().get_value())

    def get_record(self, module_api_name: str, record_id: int, fields: List) -> Dict:
        """
        Get Zoho CRM record with given id and fields list.

        :param module_api_name: str The API Name of the module to get records.
        :param record_id: int Record id for getting.
        :param fields: list Fields list.
        """
        record_operations: RecordOperations = RecordOperations()
        param_instance: ParameterMap = ParameterMap()
        for field in fields:
            param_instance.add(GetRecordParam.fields, field)
        header_instance: HeaderMap = HeaderMap()
        response: APIResponse = record_operations.get_record(
            record_id, module_api_name, param_instance, header_instance
        )
        if settings.DEBUG:
            self.display_response(response)
        if response:
            if response.get_status_code() in [204, 304]:
                return dict()
            if response_object := response.get_object():
                if isinstance(response_object, ResponseWrapper):
                    record_list = response_object.get_data()
                    return record_list[0].get_key_values()
        return dict()

    @sync_to_async(thread_sensitive=False)
    def get_records(self, module_api_name: str, fields: List, id_list: List) -> Optional[List]:
        """
        Fetch module records with specified fields names and fields id list.

        :param module_api_name: str Module name.
        :param fields: list[str] Fields name list.
        :param id_list: list[int] Fields id list.
        """
        record_operations = RecordOperations()
        param_instance = ParameterMap()
        for field_id in id_list:
            param_instance.add(GetRecordsParam.ids, field_id)
        for field in fields:
            param_instance.add(GetRecordsParam.fields, field)
        header_instance = HeaderMap()
        response = record_operations.get_records(
            module_api_name, param_instance, header_instance
        )
        if response:
            if response.get_status_code() in [204, 304]:
                return []
            if response_object := response.get_object():
                if isinstance(response_object, ResponseWrapper):
                    record_list = response_object.get_data()
                    return [record.get_key_values() for record in record_list]
        return []

    @sync_to_async(thread_sensitive=False)
    def create_records(
        self,
        module_api_name: str,
        data: List[Dict],
        photo: Union[Iterator[bytes], None] = None,
    ) -> Union[int, bool]:
        """
        Create records of a module and print the response.

        :param module_api_name: The API Name of the module to create records.
        :param data: dict with email, username, phone_number key-value pairs
        module_api_name = 'customers'

        Returns:
            ID of the created records
            False if there is any error.
        """
        record_operations: RecordOperations = RecordOperations()

        request: BodyWrapper = BodyWrapper()

        records_list: list = []

        for element in data:
            record: ZCRMRecord = ZCRMRecord()

            """
            Call add_key_value method that takes two arguments
            1 -> A string that is the Field's API Name
            2 -> Value
            """
            for key, value in element.items():
                record.add_key_value(key, value)

            record_owner: User = User()

            record_owner.set_email(os.getenv("ZOHO_CURRENT_USER_EMAIL"))

            record.add_key_value("Owner", record_owner)

            records_list.append(record)

        request.set_data(records_list)

        header_instance: HeaderMap = HeaderMap()

        response: APIResponse = record_operations.create_records(
            module_api_name, request, header_instance
        )

        if settings.DEBUG:
            self.display_response(response)

        if response:
            response_object: object = response.get_object()
            if response_object:
                if isinstance(response_object, ActionWrapper):
                    action_response_list: list = response_object.get_data()
                    for action_response in action_response_list:
                        if isinstance(action_response, SuccessResponse):
                            details: dict = action_response.get_details()
                            if photo:
                                photo_upload_response = image_handler.upload_record_photo(
                                    module_api_name,
                                    int(details.get("id")),
                                    photo,
                                )
                                if photo_upload_response:
                                    return int(details.get("id"))
                            return int(details.get("id"))
        return False

    def update_record(self, module_api_name: str, record_id: int, data: Dict) -> Optional[int]:
        """
        Update a single record of a module with ID and print the response.

        :param module_api_name: The API Name of the record's module.
        :param record_id: The ID of the record to be updated.
        :param data: Dict with fields name and it's value to update.
        example
        module_api_name = 'customers'
        record_id = 34770616603276
        data = {'Last_Activity_Time': datetime.now()}
        """
        record_operations: RecordOperations = RecordOperations()

        request: BodyWrapper = BodyWrapper()

        records_list: list = []

        record: ZCRMRecord = ZCRMRecord()

        for key, value in data.items():
            record.add_key_value(key, value)

        records_list.append(record)

        request.set_data(records_list)

        header_instance: HeaderMap = HeaderMap()

        response: APIResponse = record_operations.update_record(
            record_id, module_api_name, request, header_instance
        )
        if settings.DEBUG:
            self.display_response(response)

        return self.get_user_id(response)  # TODO add APIexception handling

    def delete_record(self, module_api_name: str, record_id: int) -> bool:
        """
        Delete a single record of a module with ID and print the response.

        :param module_api_name: The API Name of the record's module.
        :param record_id: The ID of the record to be deleted
        example
        module_api_name = 'customers'
        record_id = 34770616603276
        """
        record_operations: RecordOperations = RecordOperations()

        param_instance: ParameterMap = ParameterMap()

        param_instance.add(DeleteRecordParam.wf_trigger, True)

        header_instance: HeaderMap = HeaderMap()

        response: APIResponse = record_operations.delete_record(
            record_id, module_api_name, param_instance, header_instance
        )

        if settings.DEBUG:
            self.display_response(response)

        if response:
            response_object: object = response.get_object()
            if response_object:
                if isinstance(response_object, ActionWrapper):
                    action_response_list: list = response_object.get_data()
                    for action_response in action_response_list:
                        if isinstance(action_response, SuccessResponse):
                            return True
        return False

    def search_records(self, module_name: str, fields: List, criteria: str) -> List:
        """Search instances in Zoho CRM module."""
        record_operations = RecordOperations()
        param_instance = ParameterMap()
        for field in fields:
            param_instance.add(SearchRecordsParam.fields, field)
        param_instance.add(SearchRecordsParam.criteria, criteria)
        header_instance = HeaderMap()
        response = record_operations.search_records(
            module_name, param_instance, header_instance
        )
        result = []
        if settings.DEBUG:
            self.display_response(response)
        if response:
            if response.get_status_code() in [204, 304]:
                return result
            response_object: object = response.get_object()
            if response_object:
                if isinstance(response_object, ResponseWrapper):
                    action_response_list: list = response_object.get_data()
                    for action_response in action_response_list:
                        result.append(action_response.get_key_values())
        return result

    @staticmethod
    def get_file(record_id: int, destination_folder: str) -> str:
        """
        Get file from Zoho CRM and save file to specified folder.

        :param record_id: int Record id in Zoho CRM.
        :param destination_folder: str Destination folder name.
        """
        file_operations = FileOperations()
        param_instance = ParameterMap()
        param_instance.add(GetFileParam.id, record_id)
        response: APIResponse = file_operations.get_file(param_instance)
        filename: str = ""
        if settings.DEBUG:
            if response:
                print("Status Code: " + str(response.get_status_code()))
                if response.get_status_code() in [204, 304]:
                    print("No Content" if response.get_status_code() == 204 else "Not Modified")
                    return filename
                response_object = response.get_object()
                if not response_object:
                    if isinstance(response_object, APIException):
                        print("Status: " + response_object.get_status().get_value())
                        print("Code: " + response_object.get_code().get_value())
                        print("Details")
                        details = response_object.get_details()
                        for key, value in details.items():
                            print(key + " : " + str(value))
                        print("Message: " + response_object.get_message().get_value())
        if response:
            if response.get_status_code() in [204, 304]:
                return filename
            response_object = response.get_object()
            if response_object:
                if isinstance(response_object, FileBodyWrapper) or True:
                    stream_wrapper = response_object.get_file()
                    file_name: str = os.path.join(destination_folder, stream_wrapper.get_name())
                    with open(file_name, "wb") as f:
                        for chunk in stream_wrapper.get_stream():
                            f.write(chunk)
                        f.close()
        return filename


custom_record_operations = CustomRecord()


class CoqlQueryExecutor:
    """Class for executing COQL queries using Zoho CRM API."""

    def __init__(self):
        """Initialize the COQL query executor with an APIHTTPConnector."""
        self.connector = APIHTTPConnector()
        self.connector.url = Constants.COQL_REQUEST_URL
        self.connector.headers["Content-Type"] = "application/json"

    async def async_execute_query(self, query: str) -> dict:
        """
        Execute the COQL query and returns the response as a dictionary.

        :param query: The COQL command to execute.
        :return: A dictionary representing the response.
        """
        with ThreadPoolExecutor() as executor:
            executor.submit(Initializer.get_initializer().token.authenticate, self.connector)
        async with httpx.AsyncClient(headers=self.connector.headers) as client:
            response = await client.post(url=self.connector.url, json={"select_query": query})
        if response.content:
            return response.json()
        return {}

    async def fetch_data(self, query: str, lim: int = 200, offs: int = 0) -> List:
        """Fetch data from Zoho CRM with given query."""
        result: List = []
        limit: int = lim
        offset: int = offs
        flag: bool = True
        while flag:
            data_query: str = query + f" limit {offset}, {limit}"
            response: Dict = await self.async_execute_query(data_query)
            if (data := response.get("data")) and response.get("info"):
                result += data
                offset += limit
                flag = response.get("info").get("more_records") if lim == 200 else False
            else:
                flag = False
        return result


coql_query_executor = CoqlQueryExecutor()


class CRMImageDownloader:
    """Class for image downloading functionality."""

    def __init__(self):
        """Initialize image loader with an APIHTTPConnector."""
        self.connector = APIHTTPConnector()
        self.connector.url = Constants.COQL_REQUEST_URL

    async def perform_request(
        self, url: str, file_name: str, client: httpx.AsyncClient
    ) -> bool:
        """Perform http request and save file in case of success."""
        with ThreadPoolExecutor() as executor:
            executor.submit(Initializer.get_initializer().token.authenticate, self.connector)
        response = await client.get(url, headers=self.connector.headers)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(f"media/{file_name}"), exist_ok=True)
            with open(f"media/{file_name}", "wb") as f:
                for chunk in response.iter_bytes(chunk_size=1024):
                    f.write(chunk)
            return True
        return False

    async def download_zoho_crm_attachment_file(
        self,
        module_api_name: str,
        record_id: str,
        attachment_id: str,
        item_slug: str,
        file_name: str,
        client: httpx.AsyncClient,
    ) -> str:
        """
        Download Zoho CRM attachment file with given attachment id.

        Save file as 'media/module_api_name/product_name/file_name'.
        :param module_api_name: str Module API name.
        :param record_id: str Record id.
        :param attachment_id: str Attachment file id.
        :param item_slug: str Product slug to use in path.
        :param file_name: str File name to use in path.
        :param client: httpx.AsyncClient.

        Returns file name of the image or empty line if there is a fail of downloading.
        """
        db_file_path = f"{module_api_name}/{item_slug}/{file_name}"
        url = (
            f"https://www.zohoapis.eu/crm/v5/{module_api_name}/{record_id}"
            f"/actions/download_fields_attachment?fields_attachment_id={attachment_id}"
        )
        if await self.perform_request(url, db_file_path, client):
            return db_file_path
        return ""

    async def download_subcategory_photo(
        self, subcategory: dict[str, str], client: httpx.AsyncClient
    ) -> list[int] | dict[str, str]:
        """
        To download and save subcategories images in OS.

        Saves images in PNG.

        Returns:
            failed_subcategories: List[Dict[str, str]] - subcategories w/o images.
            images_paths: Dict[str, str] - subcategory id as key, image path as value.
        """
        db_file_path = f"subcategories/{subcategory['slug']}.png"
        url = f"https://www.zohoapis.eu/crm/v5/subcategories/{subcategory['id']}/photo"
        if await self.perform_request(url, db_file_path, client):
            return {
                "id": subcategory["id"],
                "path": db_file_path,
                "slug": subcategory["slug"],
            }
        else:
            return {
                "id": subcategory["id"],
                "path": None,
                "slug": subcategory["slug"],
            }

    def upload_record_photo(
        self,
        module_api_name: str,
        record_id: int,
        photo=None,
    ) -> bool:
        """
        To upload a photo to a record in the Zoho CRM module.

        :param photo: Iterator[bytes], data of the image to upload.
        :param photo_name: str, the name of the image file.
        :param module_api_name: str, the API name of the Zoho CRM module.
        :param record_id: int, the identifier of the record.

        :return: bool, True if created, False if not.
        """
        # Initializer.get_initializer().token.authenticate(self.connector)
        # print(self.connector.headers)
        # with requests.Session() as session:
        #     # Отправьте POST-запрос с чанками изображения
        #     response = session.post(
        #         f"https://www.zohoapis.com/crm/v2/{module_api_name}/{record_id}/photo",
        #         files={"file": photo},
        #         headers=self.connector.headers,
        #     )
        #     if response is not None:
        #         pprint(response.json())
        #         return response.json()
        # return False

        record_operations = RecordOperations()
        db_file_name = f"individual_orders/{module_api_name}/{record_id}/{photo.name}"
        os.makedirs(os.path.dirname(f"media/{db_file_name}"), exist_ok=True)
        with open(f"media/{db_file_name}", "wb") as f:
            for chunk in photo.chunks():
                f.write(chunk)

        stream_wrapper = StreamWrapper(stream=open(f"media/{db_file_name}", "rb"))
        request = FileBodyWrapper()
        request.set_file(stream_wrapper)
        response = record_operations.upload_photo(record_id, module_api_name, request)
        if response is not None:
            print("Status Code: " + str(response.get_status_code()))
            response_object = response.get_object()
            if response_object is not None:
                if isinstance(response_object, SuccessResponse):
                    print("Status: " + response_object.get_status().get_value())
                    print("Code: " + response_object.get_code().get_value())
                    print("Details")
                    details = response_object.get_details()
                    for key, value in details.items():
                        print(key + " : " + str(value))
                    print("Message: " + response_object.get_message().get_value())
                    return True

                # Check if the request returned an exception
                elif isinstance(response_object, APIException):
                    # Get the Status
                    print("Status: " + response_object.get_status().get_value())

                    # Get the Code
                    print("Code: " + response_object.get_code().get_value())

                    print("Details")

                    # Get the details dict
                    details = response_object.get_details()

                    for key, value in details.items():
                        print(key + " : " + str(value))
                    print("Message: " + response_object.get_message().get_value())
        return False


image_handler = CRMImageDownloader()
