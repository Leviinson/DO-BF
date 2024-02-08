"""Module for testing products.app_services.product_handlers functionality."""
from collections import ChainMap
from typing import Dict, List, Set, Tuple
from unittest.mock import MagicMock, patch

import pytest
from django.db.models import QuerySet
from faker import Faker

from products.app_services.product_handlers import product_detail_handlers
from products.models import ZohoImage, ZohoModuleRecord
from tests import settings
from tests.products.app_services.conftest import compare_dict
from tests.products.factories import ZohoImageFactory, ZohoModuleRecordFactory


class TestGetProductDetailsForProductView:
    """Class for test product_detail_handlers.get_product_details_for_product_view."""

    @patch(
        "products.app_services.crm_entities_interaction."
        "product_detail_operations.fetch_product_details"
    )
    def test_get_product_details_for_product_view_not_bouquet(
        self,
        get_mock: MagicMock,
        create_single_product_fake_data: Tuple[Dict, Dict],
        faker: Faker,
    ) -> None:
        """Test get_product_details_for_product_view."""
        product_dict = create_single_product_fake_data[1]
        product_dict["is_bouquet"] = False
        get_mock.return_value = product_dict
        slug = faker.slug()
        response = product_detail_handlers.get_product_details_for_product_view(
            slug, slug, slug
        )
        for key, value in product_dict.items():
            assert response[key] == value

    @patch(
        "products.app_services.crm_entities_interaction."
        "product_detail_operations.fetch_product_bouquet_data"
    )
    @patch(
        "products.app_services.crm_entities_interaction."
        "product_detail_operations.fetch_product_details"
    )
    def test_get_product_details_for_product_view_bouquet(
        self,
        get_mock_product: MagicMock,
        get_mock_bouquet: MagicMock,
        create_single_product_fake_data: Tuple[Dict, Dict],
        create_single_product_fake_bouquet_data: Tuple[List[Dict], Dict],
        faker: Faker,
    ) -> None:
        """Test get_product_details_for_product_view."""
        product_dict = create_single_product_fake_data[1]
        bouquet_dict = create_single_product_fake_bouquet_data[1]
        product_dict["is_bouquet"] = True
        get_mock_product.return_value = product_dict
        get_mock_bouquet.return_value = bouquet_dict
        slug = faker.slug()
        response = product_detail_handlers.get_product_details_for_product_view(
            slug, slug, slug
        )
        for key, value in ChainMap(product_dict, bouquet_dict).items():
            assert response[key] == value

    @patch(
        "products.app_services.crm_entities_interaction."
        "product_detail_operations.fetch_product_details"
    )
    def test_get_product_details_for_product_view_empty(
        self,
        get_mock: MagicMock,
        faker: Faker,
    ) -> None:
        """Test get_product_details_for_product_view."""
        get_mock.return_value = dict()
        slug = faker.slug()
        response = product_detail_handlers.get_product_details_for_product_view(
            slug, slug, slug
        )
        assert not response
        assert isinstance(response, Dict)


class TestGetFirstNineSubcategoryProducts:
    """Class for test product_detail_handlers.get_first_nine_subcategory_products."""

    @patch("services.image_handlers.image_handlers.embed_products_image")
    @patch(
        "products.app_services.crm_entities_interaction."
        "product_detail_operations.fetch_first_subcategory_products"
    )
    def test_get_first_nine_subcategory_products(
        self,
        get_mock_products: MagicMock,
        get_mock_images: MagicMock,
        create_fake_products: List[Dict],
        faker: Faker,
    ) -> None:
        """Test get_product_details_for_product_view."""
        products: List = create_fake_products
        get_mock_products.return_value = products
        get_mock_images.side_effect = lambda x: x
        slug = faker.slug()
        response = product_detail_handlers.get_first_nine_subcategory_products(
            slug, slug, slug, None, None
        )
        for i, product in enumerate(products):
            for key, value in product.items():
                assert response[i][key] == value

    @patch(
        "products.app_services.crm_entities_interaction."
        "product_detail_operations.fetch_first_subcategory_products"
    )
    def test_get_first_nine_subcategory_products_empty(
        self,
        get_mock_products: MagicMock,
        faker: Faker,
    ) -> None:
        """Test get_product_details_for_product_view."""
        get_mock_products.return_value = []
        slug = faker.slug()
        response = product_detail_handlers.get_first_nine_subcategory_products(
            slug, slug, slug, None, None
        )
        assert not response
        assert isinstance(response, List)

    @patch("services.image_handlers.image_handlers.embed_products_image")
    @patch(
        "products.app_services.crm_entities_interaction."
        "product_detail_operations.fetch_first_products_bouquets"
    )
    def test_get_first_nine_subcategory_products_bouquets(
        self,
        get_mock_products: MagicMock,
        get_mock_images: MagicMock,
        create_fake_products_bouquets: List[Dict],
        faker: Faker,
    ) -> None:
        """Test get_product_details_for_product_view."""
        input_products, output_products = create_fake_products_bouquets
        input_products[5]["colors"], output_products[5]["colors"] = ["aa"], ["aa"]
        input_products[9]["colors"], output_products[9]["colors"] = ["xx"], ["xx"]
        input_products[7]["flowers"], output_products[7]["flowers"] = ["yy"], ["yy"]
        input_products[8]["flowers"], output_products[8]["flowers"] = ["ww"], ["ww"]
        get_mock_products.return_value = input_products
        get_mock_images.side_effect = lambda x: x
        slug = faker.slug()
        response = product_detail_handlers.get_first_nine_subcategory_products(
            slug, "bouquets", slug, ["aa", "xx"], ["yy", "ww"]
        )
        assert len(response) == 9
        assert isinstance(response, List)
        for i, j in [(7, 0), (8, 1), (5, 2), (9, 3)]:
            compare_dict(output_products, response, i, j)

    @patch(
        "products.app_services.crm_entities_interaction."
        "product_detail_operations.fetch_first_products_bouquets"
    )
    def test_get_first_nine_subcategory_products_bouquets_empty(
        self,
        get_mock_products: MagicMock,
        faker: Faker,
    ) -> None:
        """Test get_product_details_for_product_view."""
        get_mock_products.return_value = []
        slug = faker.slug()
        response = product_detail_handlers.get_first_nine_subcategory_products(
            slug, "bouquets", slug, [slug], [slug]
        )
        assert not response
        assert isinstance(response, List)


class TestGetProductViewImgIdList:
    """Class for testing product_detail_handlers.get_product_view_img_id_list."""

    @patch("services.crm_interface.custom_record_operations.get_record")
    def test_get_product_view_img_id_list(
        self,
        get_mock: MagicMock,
        get_fake_id_images_response_and_test_data: Tuple[List[Tuple], Dict],
        faker: Faker,
    ) -> None:
        """Test get_product_view_img_id_list."""
        input_list, internal_response = get_fake_id_images_response_and_test_data
        get_mock.return_value = internal_response
        response = product_detail_handlers.get_product_view_img_id_list(
            faker.random_int(min=10)
        )
        assert len(input_list) == len(response)
        for elem in input_list:
            assert response[elem[0]] == elem[1]

    @patch("services.crm_interface.custom_record_operations.get_record")
    def test_get_product_view_img_id_list_empty(
        self,
        get_mock: MagicMock,
        faker: Faker,
    ) -> None:
        """Test get_product_view_img_id_list."""
        get_mock.return_value = dict()
        response = product_detail_handlers.get_product_view_img_id_list(
            faker.random_int(min=10)
        )
        assert not response
        assert isinstance(response, Dict)


@pytest.mark.django_db
class TestGetMissingAndOutdatedImagesIds:
    """Class for test product_detail_handlers.get_missing_and_outdated_images_ids."""

    pytestmark = pytest.mark.django_db

    @patch("os.remove")
    def test_get_missing_and_outdated_images_ids(
        self,
        get_mock: MagicMock,
        faker: Faker,
        get_fake_id_images_response_and_test_data: Tuple[List[Tuple[int, str]], Dict],
    ) -> None:
        """Test get_missing_and_outdated_images_ids."""
        get_mock.side_effect = lambda x: settings.MEDIA_URL[1:] + x[6:]
        created_zoho_image_records: List[ZohoImage] = ZohoImageFactory.create_batch(
            size=faker.random_int(min=5, max=20)
        )
        expected_ids_dict_data: Dict = get_fake_id_images_response_and_test_data[1]
        expected_ids_dict: Dict = {
            image.get_id(): image.get_file_name()
            for image in expected_ids_dict_data.get("images")
        }
        data_dict: Dict = get_fake_id_images_response_and_test_data[1]
        images_dict: Dict = {
            image.get_id(): image.get_file_name() for image in data_dict.get("images")
        }
        for i in range(3):
            images_dict[created_zoho_image_records[i].id] = created_zoho_image_records[i].image
        response = product_detail_handlers.get_missing_and_outdated_images_ids(
            images_dict, ZohoImage.objects.all()
        )
        missing_images_ids, outdated_images_ids = response
        for key in expected_ids_dict.keys():
            assert key in missing_images_ids
        assert len(missing_images_ids) == len(expected_ids_dict)
        for i in range(3, len(created_zoho_image_records)):
            assert created_zoho_image_records[i].id in outdated_images_ids
        assert len(outdated_images_ids) == len(created_zoho_image_records) - 3

    def test_get_missing_and_outdated_images_ids_empty_missing_ids_and_outdated_ids(
        self,
        faker: Faker,
        get_fake_id_images_response_and_test_data: Tuple[List[Tuple[int, str]], Dict],
    ) -> None:
        """Test get_missing_and_outdated_images_ids."""
        created_zoho_image_records: List[ZohoImage] = ZohoImageFactory.create_batch(
            size=faker.random_int(min=5, max=20)
        )
        images_dict: Dict = dict()
        for elem in created_zoho_image_records:
            images_dict[elem.id] = elem.image
        response = product_detail_handlers.get_missing_and_outdated_images_ids(
            images_dict, ZohoImage.objects.all()
        )
        missing_images_ids, outdated_images_ids = response
        assert isinstance(missing_images_ids, Set)
        assert not missing_images_ids
        assert isinstance(outdated_images_ids, Set)
        assert not outdated_images_ids

    @patch("os.remove")
    def test_get_missing_and_outdated_images_ids_empty_outdated_ids(
        self,
        get_mock: MagicMock,
        faker: Faker,
        get_fake_id_images_response_and_test_data: Tuple[List[Tuple[int, str]], Dict],
    ) -> None:
        """Test get_missing_and_outdated_images_ids."""
        get_mock.side_effect = lambda x: settings.MEDIA_URL[1:] + x[6:]
        expected_ids_dict_data: Dict = get_fake_id_images_response_and_test_data[1]
        expected_ids_dict: Dict = {
            image.get_id(): image.get_file_name()
            for image in expected_ids_dict_data.get("images")
        }
        data_dict: Dict = get_fake_id_images_response_and_test_data[1]
        images_dict: Dict = {
            image.get_id(): image.get_file_name() for image in data_dict.get("images")
        }
        response = product_detail_handlers.get_missing_and_outdated_images_ids(
            images_dict, ZohoImage.objects.all()
        )
        missing_images_ids, outdated_images_ids = response
        for key in expected_ids_dict.keys():
            assert key in missing_images_ids
        assert len(missing_images_ids) == len(expected_ids_dict)
        assert isinstance(outdated_images_ids, Set)
        assert not outdated_images_ids


@pytest.mark.django_db
class TestCreateZohoImageObjects:
    """Class for testing product_details_handlers.create_zoho_image."""

    pytestmark = pytest.mark.django_db

    @patch("services.crm_interface.image_loader.download_zoho_crm_attachment_file")
    def test_create_zoho_image_objects(
        self,
        get_mock: MagicMock,
        faker: Faker,
    ) -> None:
        """Test create_zoho_image_objects."""
        images_dict: Dict = dict()
        missing_images_ids: Set = set()
        for _ in range(faker.random_int(min=10, max=20)):
            image_id: int = faker.random_int(min=1000)
            images_dict[image_id] = faker.file_name()
            missing_images_ids.add(image_id)
        get_mock.side_effect = lambda x, y, z, a, b: images_dict.get(z)
        zoho_record_instance: ZohoModuleRecord = ZohoModuleRecordFactory()
        product_detail_handlers.create_zoho_image_objects(
            missing_images_ids,
            dict(),
            zoho_record_instance,
        )
        zoho_image_objects = ZohoImage.objects.all()
        assert len(images_dict) == len(zoho_image_objects)
        for instance in zoho_image_objects:
            assert instance.id in images_dict
            assert images_dict[instance.id] == instance.image.name

    def test_create_zoho_image_objects_empty(
        self,
        faker: Faker,
    ) -> None:
        """Test create_zoho_image_objects."""
        missing_images_ids: Set = set()
        zoho_record_instance: ZohoModuleRecord = ZohoModuleRecordFactory()
        product_detail_handlers.create_zoho_image_objects(
            missing_images_ids,
            dict(),
            zoho_record_instance,
        )
        assert not ZohoImage.objects.all()


@pytest.mark.django_db
class TestDeleteZohoImageInstances:
    """Class for testing product_details_handler.delete_zoho_image_instances."""

    pytestmark = pytest.mark.django_db

    def test_delete_zoho_image_instances(self, faker: Faker) -> None:
        """Test delete_zoho_image_instances."""
        ZohoImageFactory.create_batch(size=5)
        zoho_images_for_deletion: List[ZohoImage] = ZohoImageFactory.create_batch(size=5)
        outdated_images_ids: Set = {image.id for image in zoho_images_for_deletion}
        product_detail_handlers.delete_zoho_image_instances(outdated_images_ids)
        zoho_images_left: QuerySet = ZohoImage.objects.all()
        for instance in zoho_images_left:
            assert instance.id not in outdated_images_ids

    def test_delete_zoho_image_instances_empty(self, faker: Faker) -> None:
        """Test delete_zoho_image_instances."""
        ZohoImageFactory.create_batch(size=5)
        outdated_images_ids: Set = set()
        product_detail_handlers.delete_zoho_image_instances(outdated_images_ids)
        zoho_images_left: QuerySet = ZohoImage.objects.all()
        assert len(zoho_images_left) == 5


@pytest.mark.django_db
class TestGetProductImageList:
    """Class for testing product_details_handler.get_product_image_list."""

    pytestmark = pytest.mark.django_db

    @patch(
        "products.app_services.product_handlers."
        "product_detail_handlers.get_product_view_img_id_list"
    )
    def test_get_product_image_list(
        self,
        get_mock: MagicMock,
        faker: Faker,
    ) -> None:
        """Test get_product_image_list."""
        zoho_record_instance: ZohoModuleRecord = ZohoModuleRecordFactory()
        images_instances: List[ZohoImage] = ZohoImageFactory.create_batch(
            size=5, zoho_record=zoho_record_instance
        )
        ZohoImageFactory.create_batch(size=5)
        get_mock.return_value = {elem.id: elem.image.name for elem in images_instances}
        expected_result: QuerySet = ZohoImage.objects.filter(
            zoho_record=zoho_record_instance.id
        ).order_by("id")
        response = product_detail_handlers.get_product_image_list(zoho_record_instance)
        for i, elem in enumerate(expected_result):
            assert elem.id == response[i].id
            assert elem.image.name == response[i].image.name

    @patch(
        "products.app_services.product_handlers."
        "product_detail_handlers.get_product_view_img_id_list"
    )
    def test_get_product_image_list_empty_zoho_dict(
        self,
        get_mock: MagicMock,
        faker: Faker,
    ) -> None:
        """Test get_product_image_list."""
        zoho_record_instance: ZohoModuleRecord = ZohoModuleRecordFactory()
        ZohoImageFactory.create_batch(size=5, zoho_record=zoho_record_instance)
        ZohoImageFactory.create_batch(size=5)
        get_mock.return_value = dict()
        expected_result: QuerySet = ZohoImage.objects.filter(
            zoho_record=zoho_record_instance.id
        ).order_by("id")
        response = product_detail_handlers.get_product_image_list(zoho_record_instance)
        for i, elem in enumerate(expected_result):
            assert elem.id == response[i].id
            assert elem.image.name == response[i].image.name

    @patch("services.crm_interface.image_loader.download_zoho_crm_attachment_file")
    @patch(
        "products.app_services.product_handlers."
        "product_detail_handlers.get_product_view_img_id_list"
    )
    def test_get_product_image_list_img_not_present_in_local_db(
        self,
        get_mock_1: MagicMock,
        get_mock_2: MagicMock,
        faker: Faker,
    ) -> None:
        """Test get_product_image_list."""
        zoho_record_instance: ZohoModuleRecord = ZohoModuleRecordFactory()
        images_dict: Dict = {faker.random_int(min=1000): faker.file_name() for _ in range(5)}
        ZohoImageFactory.create_batch(size=5)
        get_mock_1.return_value = images_dict
        get_mock_2.side_effect = lambda x, y, z, a, b: b
        expected_result: QuerySet = ZohoImage.objects.filter(
            zoho_record=zoho_record_instance.id
        ).order_by("id")
        created_instances: QuerySet = ZohoImage.objects.filter(zoho_record=zoho_record_instance)
        response = product_detail_handlers.get_product_image_list(zoho_record_instance)
        for i, elem in enumerate(expected_result):
            assert elem.id == response[i].id
            assert elem.image.name == response[i].image.name
        for instance in created_instances:
            assert images_dict[instance.id] == instance.image.name


@pytest.mark.django_db
class TestCreateAndSaveProductImageFiles:
    """Class for testing product_detail_handler.create_and_save_product_image_files."""

    pytestmark = pytest.mark.django_db

    @patch(
        "products.app_services.product_handlers."
        "product_detail_handlers.get_product_view_img_id_list"
    )
    @patch("services.crm_interface.image_loader.download_zoho_crm_attachment_file")
    def test_create_and_save_product_image_files(
        self,
        get_mock_get_product_list: MagicMock,
        get_mock_image_loader: MagicMock,
        faker: Faker,
    ) -> None:
        """Test create_and_save_product_image_files."""
        images_dict: Dict = {faker.random_int(min=1000): faker.file_name() for _ in range(5)}
        get_mock_image_loader.return_value = images_dict
        get_mock_get_product_list.side_effect = lambda x, y, z, a, b: b
        product_id: int = faker.random_int(min=200)
        product_slug: str = faker.pystr(min_chars=3, max_chars=50)
        response = product_detail_handlers.create_and_save_product_image_files(
            product_id, product_slug
        )
        zoho_product_record_instance: ZohoModuleRecord = ZohoModuleRecord.objects.get(
            id=product_id
        )
        assert zoho_product_record_instance.record_name == product_slug
        assert zoho_product_record_instance.module_name == "products_base"
        assert isinstance(response, List)
        assert len(response) == len(images_dict)
        for instance in response:
            assert instance.id in images_dict
            assert images_dict[instance.id] == instance.image.name

    @patch(
        "products.app_services.product_handlers."
        "product_detail_handlers.get_product_view_img_id_list"
    )
    @patch("services.crm_interface.image_loader.download_zoho_crm_attachment_file")
    def test_create_and_save_product_image_files_empty_images_dict(
        self,
        get_mock_get_product_list: MagicMock,
        get_mock_image_loader: MagicMock,
        faker: Faker,
    ) -> None:
        """Test create_and_save_product_image_files."""
        get_mock_image_loader.return_value = dict()
        get_mock_get_product_list.side_effect = lambda x, y, z, a, b: b
        product_id: int = faker.random_int(min=200)
        product_slug: str = faker.pystr(min_chars=3, max_chars=50)
        response = product_detail_handlers.create_and_save_product_image_files(
            product_id, product_slug
        )
        zoho_product_record_instance: ZohoModuleRecord = ZohoModuleRecord.objects.get(
            id=product_id
        )
        assert zoho_product_record_instance.record_name == product_slug
        assert zoho_product_record_instance.module_name == "products_base"
        assert isinstance(response, List)
        assert not response

    @patch(
        "products.app_services.product_handlers."
        "product_detail_handlers.get_product_view_img_id_list"
    )
    @patch("services.crm_interface.image_loader.download_zoho_crm_attachment_file")
    def test_create_and_save_product_image_files_without_db_file_name(
        self,
        get_mock_get_product_list: MagicMock,
        get_mock_image_loader: MagicMock,
        faker: Faker,
    ) -> None:
        """Test create_and_save_product_image_files."""
        images_dict: Dict = {faker.random_int(min=1000): faker.file_name() for _ in range(5)}
        get_mock_image_loader.return_value = images_dict
        get_mock_get_product_list.return_value = ""
        product_id: int = faker.random_int(min=200)
        product_slug: str = faker.pystr(min_chars=3, max_chars=50)
        response = product_detail_handlers.create_and_save_product_image_files(
            product_id, product_slug
        )
        zoho_product_record_instance: ZohoModuleRecord = ZohoModuleRecord.objects.get(
            id=product_id
        )
        assert zoho_product_record_instance.record_name == product_slug
        assert zoho_product_record_instance.module_name == "products_base"
        assert isinstance(response, List)
        assert not response
