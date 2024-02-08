"""Handlers for fetching and saving Zoho CRM images."""
import asyncio
import os
from collections import defaultdict, namedtuple
from typing import Dict, List, Set, Tuple

import httpx
from django.db.models import QuerySet

from products.models import ZohoImage, ZohoModuleRecord
from services.crm_interface import custom_record_operations, image_handler


class ProductImageHandler:
    """Handler for getting images for products."""

    Image: Tuple = namedtuple("Image", ["id", "slug", "file_name"])

    async def embed_products_image(
        self, data_list: List[Dict], is_many: bool = False, **kwargs
    ) -> List[Dict]:
        """
        Add image key/value to dict.

        :param data_list: list[dict] Data dicts list.
        :param is_many: bool Tells whether we need to fetch all possible images to
            every products or the first one.
        """
        if data_list:
            data_with_images = await custom_record_operations.get_records(
                "products_base",
                ["id", "images", "slug"],
                [item.get("id") for item in data_list],
            )
            images_dict = await self.get_or_load_and_create_images(data_with_images, is_many)
            self.insert_images_in_data_dicts(data_list, images_dict, is_many)
        return data_list

    async def get_or_load_and_create_images(
        self, data_images: List[Dict], is_many: bool
    ) -> Dict:
        """
        Get product image data from local db.

        If Zoho CRM products list contains images not present in local db,
        load them in local db.
        :param data_images: list[dict] Products with images field.
        :param is_many: bool Is many images or first one needed.
        """
        images_dict: Dict = self.create_images_dict(data_images, is_many)
        local_images: List = await ZohoImage.avalues_list(id__in=images_dict)
        if len(local_images) != len(images_dict):
            images_dict, outdated_ids = self.get_missing_and_outdated_images_ids(
                images_dict=images_dict, saved_images=local_images
            )
            local_images.extend(await self.create_images_in_local_db(images_dict))
            await self.delete_zoho_image_instances(outdated_ids)
        return await self.create_products_images_dict(local_images)

    @staticmethod
    def insert_images_in_data_dicts(
        products_list: List[Dict], images_dict: Dict, is_many: bool
    ) -> List[Dict]:
        """
        Insert images into products list dicts.

        Delete, if there is, unused 'images' keys.
        """
        for item in products_list:
            if values := images_dict.get(int(item.get("id")), list()):
                if not is_many:
                    item["image"] = values[0]
                    item.pop("images", None)
                    continue
            item["images"] = values
        return products_list

    @staticmethod
    async def create_products_images_dict(local_images: QuerySet | List) -> Dict:
        """
        Create dict with product_id/product_images_list as key/values.

        :param local_images: Queryset with local images.
        """
        products_images_dict: Dict = defaultdict(list)
        for image in local_images:
            products_images_dict[image.zoho_record_id].append(image.image)
        return products_images_dict

    async def create_images_in_local_db(self, images_dict: Dict) -> List:
        """
        Check whether input dicts have equal length.

        If they don't have, load and save not stored images in local db.
        :param images_dict: Dict Loaded images data from Zoho CRM.
        """
        files_names = await self.download_images_and_get_files_names(images_dict)
        images_ids_and_data = zip(images_dict.keys(), images_dict.values())
        image_objects: List = await self.get_downloaded_images_objects_list(
            files_names, images_ids_and_data
        )
        return await ZohoImage.objects.abulk_create(image_objects)

    @staticmethod
    async def download_images_and_get_files_names(
        images_dict: Dict,
    ) -> Tuple[
        str | BaseException,
        str | BaseException,
        str | BaseException,
        str | BaseException,
        str | BaseException,
    ]:
        """
        To create 'image_handler.download_zoho_crm_attachment_file' coroutines list.

        Executes coroutines in the 'asyncio.gather' method.

        Returns list of coroutines results.
        """
        coroutines = []

        async with httpx.AsyncClient(headers=image_handler.connector.headers) as client:
            for image_id, image_data in images_dict.items():
                coroutines.append(
                    image_handler.download_zoho_crm_attachment_file(
                        "products_base",
                        str(image_data.id),
                        str(image_id),
                        image_data.slug,
                        image_data.file_name,
                        client,
                    )
                )
            return await asyncio.gather(*coroutines)

    @staticmethod
    async def get_downloaded_images_objects_list(
        files_names: Tuple[
            str | BaseException,
            str | BaseException,
            str | BaseException,
            str | BaseException,
            str | BaseException,
        ],
        images_ids_and_data,
    ) -> List:
        """To save images as records locally in DB."""
        result = []
        for file_name, (image_id, image_data) in zip(files_names, images_ids_and_data):
            zoho_module_record = await ZohoModuleRecord.objects.aget_or_create(
                id=image_data.id,
                module_name="products_base",
                record_name=image_data.slug,
            )
            if file_name:
                result.append(
                    ZohoImage(
                        id=image_id,
                        zoho_record=zoho_module_record[0],
                        image=file_name,
                    )
                )
        return result

    @staticmethod
    async def delete_zoho_image_instances(outdated_images_ids: Set[int]) -> None:
        """
        Delete ZohoImage instances with ids in outdated_images_ids.

        :param outdated_images_ids: set[int] Set with instances id.
        """
        await ZohoImage.objects.filter(id__in=outdated_images_ids).adelete()

    @staticmethod
    def get_missing_and_outdated_images_ids(
        images_dict: Dict[int, str], saved_images: List
    ) -> Tuple[Dict, Set[int]]:
        """
        Create missing_images_ids and outdated_images_ids.

        The first one is with image ids not presented in local db,
        the second one is with image ids that is not needed and have to be deleted.
        :param images_dict: dict Dict with image id as key and image file name as value
        for given product.
        :param saved_images: QuerySet Object with images that is connected to product
        with given id.
        """
        outdated_images_ids: Set = set()
        for image in saved_images:
            if image.id not in images_dict:
                outdated_images_ids.add(image.id)
                os.remove(f"media/{image.image}")
            else:
                images_dict.pop(image.id)
        return images_dict, outdated_images_ids

    def create_images_dict(self, items: List[Dict], is_many: bool) -> Dict:
        """
        Create dict with Zoho image id as key.

        Value will be namedtuple with products id and Name.
        :param items: list[dict] Items dict list.
        :param is_many: bool Is many images or first one needed.
        """
        images_dict = dict()
        for item in items:
            if images := item.get("images"):
                for image in images:
                    images_dict[int(image.get_id())] = self.Image(
                        id=int(item.get("id")),
                        slug=item.get("slug"),
                        file_name=image.get_file_name(),
                    )
                    if not is_many:
                        break
        return images_dict


product_image_handler = ProductImageHandler()


class SubcategoryImageHandler:
    """Handler for getting images for subcategories."""

    async def embed_subcategories_images(
        self,
        subcategories: List[Dict[str, str]],
    ):
        """
        To download and save images in DB and OS of the subcategories.

        Uses requests to the ZohoCRM API.

        Returns subcategories with key "images" and address to the image.
        """
        subcategories_dict: Dict = (
            await self.create_subcategories_dict_with_refreshing_local_db(subcategories)
        )
        await self.update_subcategories_dict_with_mised_images(
            subcategories, subcategories_dict
        )
        for subcategory in subcategories:
            subcategory["image"] = subcategories_dict[subcategory["id"]]
        return subcategories

    @staticmethod
    async def create_subcategories_dict_with_refreshing_local_db(
        subcategories: List,
    ) -> Dict:
        """Create subcategories id:image dict, refreshing local db subcategories images."""
        local_db_subcategories_images = ZohoImage.objects.filter(
            zoho_record__module_name="subcategories"
        )
        images_for_deletion: List = []
        subcategories_dict: Dict = {subcategory["id"]: None for subcategory in subcategories}
        async for image in local_db_subcategories_images:
            if image.id in subcategories_dict:
                subcategories_dict[image.id] = image
            else:
                images_for_deletion.append(image.id)
                os.remove(image.image.url[1:])
        if images_for_deletion:
            await ZohoImage.objects.filter(id__in=images_for_deletion).adelete()
        return subcategories_dict

    @staticmethod
    async def update_subcategories_dict_with_mised_images(
        subcategories: List, subcategories_dict: Dict
    ) -> Dict:
        """
        Update subcategories dict with missed images, in case there are some.

        Also download image files from Zoho CRM and save it local db.
        """
        subcategories_wo_images: List = [
            subcategory
            for subcategory in subcategories
            if not subcategories_dict.get(subcategory["id"])
        ]
        subcategories_images = []

        if subcategories_wo_images:
            coroutines = []
            async with httpx.AsyncClient() as client:
                for subcategory in subcategories_wo_images:
                    coroutines.append(
                        image_handler.download_subcategory_photo(subcategory, client)
                    )
                subcategories_photo_data = await asyncio.gather(*coroutines)
            for subcategory in subcategories_photo_data:
                zoho_record, created = await ZohoModuleRecord.objects.aget_or_create(
                    id=subcategory["id"],
                    module_name="subcategories",
                    record_name=subcategory["slug"],
                )
                if subcategory["path"]:
                    image = ZohoImage(
                        id=subcategory["id"],
                        zoho_record=zoho_record,
                        image=subcategory["path"],
                    )
                    subcategories_images.append(image)
                    subcategories_dict[subcategory["id"]] = image
            await ZohoImage.objects.abulk_create(subcategories_images)
        return subcategories_dict


subcategory_image_handler = SubcategoryImageHandler()
