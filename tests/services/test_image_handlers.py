"""Module for testing services.image_handlers."""
from collections import namedtuple
from typing import Dict, List, Tuple
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from asgiref.sync import async_to_sync
from faker import Faker

from services.image_handlers import product_image_handler

Image = namedtuple("Image", ["id", "slug", "file_name"])


@pytest.mark.django_db
class TestEmbedProductsImage:
    """Class for testing ImageHandlers embed_products_image method."""

    pytestmark = pytest.mark.django_db

    @patch(
        "services.image_handlers.image_handlers.download_images_and_get_files_names",
        new_callable=AsyncMock,
    )
    @patch("services.crm_interface.custom_record_operations.get_records")
    def test_embed_products_image(
        self,
        mock_data_with_images: MagicMock,
        mock_download_files: AsyncMock,
        faker: Faker,
        get_fake_products_data_with_images: Tuple[List[Dict], List[Dict]],
    ) -> None:
        """Test embed_products_image method."""
        products, products_with_img = get_fake_products_data_with_images
        file_names: List = []
        for product in products_with_img:
            for image in product["images"]:
                file_names.append(image.get_file_name())

        mock_data_with_images.return_value = products_with_img
        mock_download_files.return_value = file_names

        result = async_to_sync(product_image_handler.embed_products_image)(
            products, is_many=True
        )
        for i, product in enumerate(products_with_img):
            for key, value in product.items():
                if key == "images":
                    assert len(result[i]["images"]) == 3
                    for j, image in enumerate(result[i]["images"]):
                        assert value[j].get_file_name() == image.name
                else:
                    assert result[i][key] == value

    @patch(
        "services.image_handlers.image_handlers.download_images_and_get_files_names",
        new_callable=AsyncMock,
    )
    @patch("services.crm_interface.custom_record_operations.get_records")
    def test_embed_products_image_many_false(
        self,
        mock_data_with_images: MagicMock,
        mock_download_files: AsyncMock,
        faker: Faker,
        get_fake_products_data_with_images: Tuple[List[Dict], List[Dict]],
    ) -> None:
        """Test embed_products_image method. Many is False."""
        products, products_with_img = get_fake_products_data_with_images
        file_names: List = []
        for product in products_with_img:
            for image in product["images"]:
                file_names.append(image.get_file_name())
                break

        mock_data_with_images.return_value = products_with_img
        mock_download_files.return_value = file_names

        result = async_to_sync(product_image_handler.embed_products_image)(
            products, is_many=False
        )
        for i, product in enumerate(products_with_img):
            for key, value in product.items():
                if key == "images":
                    assert value[0].get_file_name() == result[i]["image"].name
                else:
                    assert result[i][key] == value


class TestCreateImagesDict:
    """Class for testing ImageHandlers create_images_dict method."""

    def test_create_images_dict(
        self,
        get_fake_products_data_with_images: Tuple[List[Dict], List[Dict]],
    ) -> None:
        """Test create_images_dict method."""
        products, products_with_images = get_fake_products_data_with_images
        result = product_image_handler.create_images_dict(products_with_images, is_many=True)
        for product in products_with_images:
            for image in product["images"]:
                img = result[image.get_id()]
                assert img.id == int(product["id"])
                assert img.slug == product["slug"]
                assert img.file_name == image.get_file_name()
        assert 3 * len(products_with_images) == len(result)

    def test_create_images_dict_many_false(
        self,
        get_fake_products_data_with_images: Tuple[List[Dict], List[Dict]],
    ) -> None:
        """Test create_images_dict method."""
        products, products_with_images = get_fake_products_data_with_images
        result = product_image_handler.create_images_dict(products_with_images, is_many=False)
        for product in products_with_images:
            for image in product["images"]:
                img = result[image.get_id()]
                assert img.id == int(product["id"])
                assert img.slug == product["slug"]
                assert img.file_name == image.get_file_name()
                break
        assert len(products_with_images) == len(result)
