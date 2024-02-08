"""Class for testing mainpage.utils functionality."""

from typing import Dict, List, Set, Tuple, Union

from faker import Faker

from mainpage.app_services.utils import quick_selection_menu


class TestSatisfyCriteria:
    """Class for testing quick_selection_menu.satisfy_criteria."""

    def test_satisfy_criteria_subcategory_in(
        self,
        create_criteria_input: Tuple[Dict, List[Union[Set, int]]],
    ) -> None:
        """
        Check whether satisfy_criteria returns True.

        Subcategory in set, default low and high.
        """
        data, criteria = create_criteria_input
        criteria[0].add(data.get("subcategory_name"))
        assert quick_selection_menu.satisfy_criteria(data, tuple(criteria))

    def test_satisfy_criteria_subcategory_in_price_in(
        self,
        create_criteria_input: Tuple[Dict, List[Union[Set, int]]],
        faker: Faker,
    ) -> None:
        """
        Check whether satisfy_criteria returns True.

        Subcategory in set, low and high out of range.
        """
        data, criteria = create_criteria_input
        criteria[0].add(data.get("subcategory_name"))
        criteria[1] = faker.random_int(min=0, max=99)
        criteria[2] = faker.random_int(min=100000000, max=1000000000000000)
        assert quick_selection_menu.satisfy_criteria(data, tuple(criteria))

    def test_satisfy_criteria_subcategory_out(
        self,
        create_criteria_input: Tuple[Dict, List[Union[Set, int]]],
        faker: Faker,
    ) -> None:
        """
        Check whether satisfy_criteria returns False.

        Subcategory not in set, low and high is default.
        """
        data, criteria = create_criteria_input
        assert not quick_selection_menu.satisfy_criteria(data, tuple(criteria))

    def test_satisfy_criteria_subcategory_in_low_is_high(
        self,
        create_criteria_input: Tuple[Dict, List[Union[Set, int]]],
        faker: Faker,
    ) -> None:
        """
        Check whether satisfy_criteria returns False.

        Subcategory in set, low is high.
        """
        data, criteria = create_criteria_input
        criteria[0].add(data.get("subcategory_name"))
        criteria[1] = faker.random_int(min=1000000000, max=10000000000)
        assert not quick_selection_menu.satisfy_criteria(data, tuple(criteria))

    def test_satisfy_criteria_subcategory_in_high_is_low(
        self,
        create_criteria_input: Tuple[Dict, List[Union[Set, int]]],
        faker: Faker,
    ) -> None:
        """
        Check whether satisfy_criteria returns False.

        Subcategory in set, high is low.
        """
        data, criteria = create_criteria_input
        criteria[0].add(data.get("subcategory_name"))
        criteria[2] = faker.random_int(max=99)
        assert not quick_selection_menu.satisfy_criteria(data, tuple(criteria))

    def test_satisfy_criteria_subcategory_not_in_price_out(
        self,
        create_criteria_input: Tuple[Dict, List[Union[Set, int]]],
        faker: Faker,
    ) -> None:
        """
        Check whether satisfy_criteria returns False.

        Subcategory in set, high is low.
        """
        data, criteria = create_criteria_input
        criteria[1] = faker.random_int(min=1000000000, max=10000000000)
        criteria[2] = faker.random_int(max=99)
        assert not quick_selection_menu.satisfy_criteria(data, tuple(criteria))


# class TestPrepareSubcategorySet:
#     """Class for testing quick_selection_menu.prepare_subcategory_set."""
#
#     @patch("services.crm_entities_handlers.subcategories_handler.fetch_instances")
#     def test_prepare_subcategory_set_empty(
#         self,
#         get_mock: MagicMock,
#         get_response_categories_list: Tuple[List[Dict], List[Dict]],
#     ) -> None:
#         """
#         Check whether method returns empty set.
#
#         Input data - None, None.
#         """
#         input_list, categories_list = get_response_categories_list
#         get_mock.return_value = categories_list
#         response = async_to_sync(quick_selection_menu.prepare_subcategory_set)(
#             category=None, subcategory=None
#         )
#         assert not response
#         assert isinstance(response, Set)

# @patch("services.caching.caching.get_categories_and_subcategories")
# def test_prepare_subcategory_set_with_category_and_subcategory(
#     self,
#     get_mock: MagicMock,
#     get_response_categories_list: Tuple[List[Dict], List[Dict]],
#     faker: Faker,
# ) -> None:
#     """
#     Check whether method returns set with one subcategory.
#
#     Input data - category and subcategory names.
#     """
#     input_list, categories_list = get_response_categories_list
#     get_mock.return_value = categories_list
#     index = faker.random_int(max=len(categories_list) - 1)
#     category: str = categories_list[index].get("Name")
#     subcategory: str = (
#         categories_list[index]
#         .get("subcategories")[
#             faker.random_int(max=len(categories_list[index].get("subcategories")) - 1)
#         ]
#         .get("Name")
#     )
#     response = async_to_sync(quick_selection_menu.prepare_subcategory_set)(
#         category, subcategory
#     )
#     assert len(response) == 1
#     assert isinstance(response, Set)
#     assert subcategory in response
#
# @patch("services.caching.caching.get_categories_and_subcategories")
# def test_prepare_subcategory_set_with_subcategory(
#     self,
#     get_mock: MagicMock,
#     get_response_categories_list: Tuple[List[Dict], List[Dict]],
#     faker: Faker,
# ) -> None:
#     """
#     Check whether method returns set with one subcategory.
#
#     Input data - category is None and subcategory name.
#     """
#     input_list, categories_list = get_response_categories_list
#     get_mock.return_value = categories_list
#     index = faker.random_int(max=len(categories_list) - 1)
#     subcategory: str = (
#         categories_list[index]
#         .get("subcategories")[
#             faker.random_int(max=len(categories_list[index].get("subcategories")))
#         ]
#         .get("Name")
#     )
#     response = async_to_sync(quick_selection_menu.prepare_subcategory_set)(
#         category=None, subcategory=subcategory
#     )
#     assert len(response) == 1
#     assert isinstance(response, Set)
#     assert subcategory in response
#
# @patch("services.caching.caching.get_categories_and_subcategories")
# def test_prepare_subcategory_set_with_category(
#     self,
#     get_mock: MagicMock,
#     get_response_categories_list: Tuple[List[Dict], List[Dict]],
#     faker: Faker,
# ) -> None:
#     """
#     Check whether method returns set with one subcategory.
#
#     Input data - category name and subcategory is None.
#     """
#     input_list, categories_list = get_response_categories_list
#     get_mock.return_value = categories_list
#     index = faker.random_int(max=len(categories_list) - 1)
#     category: str = categories_list[index].get("Name")
#     subcategory_set: Set = {
#         item.get("Name") for item in categories_list[index].get("subcategories")
#     }
#     response = async_to_sync(quick_selection_menu.prepare_subcategory_set)(
#         category=category, subcategory=None
#     )
#     assert len(response) == len(subcategory_set)
#     assert isinstance(response, Set)
#     for item in response:
#         assert item in subcategory_set
#
# @patch("services.caching.caching.get_categories_and_subcategories")
# def test_prepare_subcategory_set_with_category_not_in_categories(
#     self,
#     get_mock: MagicMock,
#     get_response_categories_list: Tuple[List[Dict], List[Dict]],
#     faker: Faker,
# ) -> None:
#     """
#     Check whether method returns set with one subcategory.
#
#     Input data - category name not in categories and subcategory is None.
#     """
#     input_list, categories_list = get_response_categories_list
#     get_mock.return_value = categories_list
#     category: str = faker.pystr(min_chars=40, max_chars=100)
#     response = async_to_sync(quick_selection_menu.prepare_subcategory_set)(
#         category=category, subcategory=None
#     )
#     assert len(response) == 1
#     assert isinstance(response, Set)
#     assert "not_exist" in response


#
# class TestGetFilteredProducts:
#     """Class for testing quick_selection_menu.get_filtered_products."""
#
#     @patch("mainpage.app_services.utils.quick_selection_menu.satisfy_criteria")
#     @patch("services.caching.caching.get_region_products")
#     def test_get_filtered_products_all(
#         self,
#         get_mock_1: MagicMock,
#         get_mock_2: MagicMock,
#         get_fake_region_products: List[Dict],
#         faker: Faker,
#     ) -> None:
#         """Check whether method returns not modified list."""
#         product_list = get_fake_region_products
#         get_mock_1.return_value = product_list
#         get_mock_2.return_value = True
#         response = quick_selection_menu.get_filtered_products(
#             region=faker.city(), criteria=({}, 0, 0)
#         )
#         for i, product in enumerate(product_list):
#             for key, value in response[i].items():
#                 assert product[key] == value
#
#     @patch("mainpage.app_services.utils.quick_selection_menu.satisfy_criteria")
#     @patch("services.caching.caching.get_region_products")
#     def test_get_filtered_products_empty(
#         self,
#         get_mock_1: MagicMock,
#         get_mock_2: MagicMock,
#         get_fake_region_products: List[Dict],
#         faker: Faker,
#     ) -> None:
#         """Check whether method returns not modified list."""
#         product_list = get_fake_region_products
#         get_mock_1.return_value = product_list
#         get_mock_2.return_value = False
#         response = quick_selection_menu.get_filtered_products(
#             region=faker.city(), criteria=({}, 0, 0)
#         )
#         assert isinstance(response, List)
#         assert not response
#
#     @patch("services.caching.caching.get_region_products")
#     def test_get_filtered_products(
#         self,
#         get_mock: MagicMock,
#         get_fake_region_products: List[Dict],
#         faker: Faker,
#     ) -> None:
#         """Check whether method returns not modified list."""
#         product_list = get_fake_region_products
#         get_mock.return_value = product_list
#         price = faker.random_int(min=100, max=1000)
#         mod_product_list = [item for item in product_list if item.get("unit_price") <= price]
#         response = quick_selection_menu.get_filtered_products(
#             region=faker.city(), criteria=({}, 0, price)
#         )
#         for i, product in enumerate(mod_product_list):
#             for key, value in response[i].items():
#                 assert product[key] == value
