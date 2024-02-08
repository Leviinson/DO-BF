"""Orders views."""

import json
import os
from enum import Enum
from typing import Any, Union
from uuid import uuid4

from django.core.mail import send_mail
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
    HttpResponseServerError,
    JsonResponse,
)
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect
from twilio.http.async_http_client import AsyncTwilioHttpClient
from twilio.rest import Client

from async_forms.async_forms import AsyncForm, AsyncModelForm
from async_views.generic.base import AsyncTemplateView
from async_views.generic.edit import AsyncFormView
from cart.app_services.session_data import session_data
from cart.app_services.utils import formatters as cart_formatters
from orders.forms import AsyncCheckoutForm
from services.common_handlers import common_handlers
from services.data_getters import crm_data
from services.mixins import ApplicationMixin
from services.utils import utilities

from .app_services.orders_handlers import (
    individual_order_handlers,
    order_handlers,
    quick_order_handlers,
)


# Create your views here.
@method_decorator(csrf_protect, name="dispatch")
class IndividualOrders(View):
    """Individual order endpoint controller."""

    async def post(self, request: HttpRequest, *args, **kwargs):
        """
        Handle POST request to create an individual order for the user in the ZohoCRM.

        :param request: The HttpRequest object.
        :param args: Any positional arguments passed to the view.
        :param kwargs: Any keyword arguments passed to the view.

        Returns:
        - JsonResponse with status 201 if the individual order is created successfully.
        - JsonResponse with status 400 if not all required data is provided, wrong type.
        - JsonResponse with status 500 if an unexpected error occurs.
        """
        data: dict[str, str] = request.POST
        min_budget, max_budget = utilities.get_min_max_budget(
            data["minBudget"], data["maxBudget"]
        )
        if min_budget is None or max_budget is None:
            return JsonResponse(
                {"msg": "Min and max budget must be decimals and are required."},
                status=400,
            )
        if not (data.get("name") and data.get("full_number")):
            return JsonResponse({"msg": "Not all data passed"}, status=400)

        photo = request.FILES.get("file")
        customer_id, customer_name, customer_phone_number = self.get_customer_info(
            request, data
        )

        if await self.create_individual_order(
            customer_id,
            customer_name,
            customer_phone_number,
            min_budget,
            max_budget,
            photo,
        ):
            return JsonResponse({}, status=201)
        return JsonResponse({"msg": "Unexpected error."}, status=500)

    def get_customer_info(
        self, request: HttpRequest, data: dict
    ) -> Union[Union[int, None], str, str]:
        """
        To get customer information based on user authentication or form data.

        :param request: The HttpRequest object.
        :param data: The request data (POST data).

        Returns:
        A tuple containing customer_id, customer_name, and customer_phone_number.
        """
        # if (user := request.user).is_authenticated:
        #     customer_id: int = user.zoho_id
        #     customer_name: str = user.username
        #     customer_phone_number: str = user.phone_number
        # else:
        customer_id = None
        customer_name: str = data.get("name")
        customer_phone_number: str = data.get("full_number")
        return customer_id, customer_name, customer_phone_number

    async def create_individual_order(
        self,
        customer_id: int,
        customer_name: str,
        customer_phone_number: str,
        min_budget: float,
        max_budget: float,
        photo,
    ) -> Union[int, bool]:
        """
        To create an individual order.

        :param customer_id: The customer's ID.
        :param customer_name: The customer's name.
        :param customer_phone_number: The customer's phone number.
        :param min_budget: The minimum budget as Decimal.
        :param max_budget: The maximum budget as Decimal.
        :param photo: The uploaded photo.

        Returns:
        The created individual order or None if the order creation fails.
        """
        if all(
            [
                customer_name,
                customer_phone_number,
                min_budget is not None,
                max_budget is not None,
            ]
        ):
            return await individual_order_handlers.create_individual_order(
                customer_id,
                customer_name,
                customer_phone_number,
                min_budget,
                max_budget,
                photo,
            )
        return False


@method_decorator(csrf_protect, name="dispatch")
class QuickOrders(View):
    """
    A class for handling quick orders.

    This class provides methods for creating quick orders in the ZohoCRM.
    """

    async def post(
        self,
        request: HttpRequest,
        *args,
        **kwargs,
    ):
        """
        Create a quick order in the ZohoCRM.

        :param product_id: The ID of the product for the quick order.
        :param customer_name: The name of the customer placing the quick order.
        :param customer_phone_number: The phone number of the customer.
        :param customer_id: The ID of the customer (if available), or None.

        Returns:
        The created quick order record in the ZohoCRM or None if the creation fails.
        """
        try:
            data: dict[str, Union[str, int]] = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"msg": "Wrong data passed"}, status=400)

        # if (user := request.user).is_authenticated:
        #     customer_id = user.zoho_id
        #     customer_name = user.username
        #     customer_phone_number = user.phone_number
        # else:
        customer_id = None
        customer_name = data.get("name")
        customer_phone_number = data.get("full_number")

        if not (product_id := data.get("productId")):
            return JsonResponse(
                {"msg": "Product ID isn't passed."},
                status=400,
            )
        if not isinstance(product_id, str):
            return JsonResponse(
                {"msg": "Product ID must be integer reduced to string"}, status=400
            )

        if not product_id.isdigit():
            return JsonResponse(
                {"msg": "Product ID isn't integer reduced to string"}, status=400
            )

        product_id = int(product_id)
        if all([customer_name, customer_phone_number]):
            if await quick_order_handlers.create_quick_order(
                product_id, customer_name, customer_phone_number, customer_id
            ):
                return JsonResponse({}, status=201)
            return JsonResponse({"msg": "Unexpected error."}, status=500)
        return JsonResponse({"msg": "Not all data passed"}, status=400)


class CheckoutView(AsyncFormView, ApplicationMixin):
    """
    View for processing checkout data.

    Attributes:
        form_class (type): The form class for the view.
        template_name (str): The template to render the view.
    """

    form_class = AsyncCheckoutForm
    template_name = "orders/checkout.html"

    async def get_context_data(self, *args, **kwargs):
        """
        Retrieve and return the context data for rendering the checkout page.

        Args:
            *args: Variable-length arguments.
            **kwargs: Keyword arguments.

        Returns:
            dict: A dictionary containing the context data.
        """
        context = await self.get_common_context(
            **await super().get_context_data(*args, **kwargs)
        )
        if isinstance(context, HttpResponseServerError):
            return context
        context["cart_products"] = cart_products = await common_handlers.get_cart_products(
            context["region"]["slug"],
            await session_data.get_or_create_cart(self.request.session),
            context["selected_currency"],
        )
        context["cart_grand_total_price"] = self.calculate_cart_grand_total(cart_products)
        await self.update_context_with_suggested_products(context, cart_products)
        return context

    async def update_context_with_cart_data(self, context):
        """
        Update the context with cart-related data.

        Args:
            context (dict): The context dictionary.
        """
        region = context["region"]
        cart: dict = await session_data.get_or_create_cart(self.request.session)
        region_products = await crm_data.get_region_products(
            region["slug"],
            currency=context["selected_currency"],
            cart_ids_set={product["id"] for product in cart["products"]},
        )
        context["cart_products"] = await cart_formatters.format_cart_products(
            cart, region_products, context["selected_currency"]
        )
        return context["cart_products"]

    def calculate_cart_grand_total(
        self, cart_products
    ):  # TODO: to combine this method with CartView._calculate_cart_grand_total_price
        """
        Calculate and add the cart grand total to the context.

        Args:
            context (dict): The context dictionary.
        """
        return round(
            sum(
                map(
                    lambda x: (x["unit_price"] if not x["discount"] else x["new_price"])
                    * x["cart_amount"],
                    cart_products,
                )
            ),
            2,
        )

    async def update_context_with_suggested_products(self, context, cart_products):
        """
        Update the context with suggested products.

        Args:
            context (dict): The context dictionary.
        """
        region = context["region"]
        region_products = await crm_data.get_region_products(
            region["slug"], currency=context["selected_currency"]
        )
        context["suggested_products"] = (
            await common_handlers.get_first_three_additional_products(
                region["slug"], region_products, cart_products
            )
        )

    async def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """
        To handle the HTTP GET request.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HttpResponse: The HTTP response object.
        """
        session = self.request.session
        cart_products = (await session_data.get_or_create_cart(session))["products"]

        if not cart_products:
            return await self.redirect_to_success_url()

        return await super().get(request, *args, **kwargs)

    async def get_cart_products(self, session):
        """
        To retrieve cart products from the session.

        Args:
            session: The session object.

        Returns:
            dict: A dictionary containing cart products.
        """

    async def redirect_to_success_url(self):
        """
        Redirects to the success URL based on region and currency.

        Returns:
            HttpResponseRedirect: The HTTP redirect response object.
        """
        region_slug = self.kwargs["region_slug"]
        currency = self.kwargs.get("currency", "UAH")
        success_url = await self.get_success_url(region_slug, currency)
        return HttpResponseRedirect(success_url)

    async def post(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> Union[TemplateResponse, HttpResponseRedirect]:
        """
        Handle POST requests.

        Instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = await self.get_form()
        if await form.async_is_valid():
            return await self.form_valid(form, self.kwargs["region_slug"])
        return await self.form_invalid(form)

    async def form_valid(
        self, form: AsyncForm | AsyncModelForm, region_slug: str
    ) -> HttpResponseRedirect:
        """
        Handle a valid form submission.

        Args:
            form (AsyncForm | AsyncModelForm): The valid form instance.

        Returns:
            HttpResponseRedirect: A redirect response to the next step in the checkout process.
        """
        data = form.cleaned_data
        currencies = await crm_data.get_currency_list(self.request)
        if isinstance(currencies, HttpResponseServerError):
            return currencies

        selected_currency = utilities.get_selected_currency(
            currencies, data.get("selected_currency")
        )
        if not selected_currency:
            return HttpResponseBadRequest(
                render(
                    self.request,
                    "templates/notification.html",
                    {
                        "header": "Bad request",
                        "message_top": "We are so sorry, but there is \
                            a problem with your request (passed currency)",
                        "message_bottom": "You can notify an owner about it",
                        "redirect_link": ".",
                        "redirect_message": "Repeat again",
                    },
                )
            )
        session = self.request.session
        cart_products = (await session_data.get_or_create_cart(session))["products"]
        if not cart_products:
            return HttpResponseRedirect(
                await self.get_success_url(region_slug, data["selected_currency"])
            )
        cart_products_ids = {product["id"] for product in cart_products}
        not_existent_products_id_set = await order_handlers.get_not_existent_products(
            cart_products_ids
        )

        if not_existent_products_id_set:
            await session_data.remove_ordered_products(session, not_existent_products_id_set)
            return render(
                self.request,
                "templates/notification.html",
                {
                    "title": "BonnyFlowers",
                    "header": "Помилка",
                    "message_top": "Продукти у Вашій корзині не співпадають з існуючими, \
                        застарілі буде видалено",
                    "message_bottom": "Перейдіть до корзини, перевірте продукти у ній \
                        та зробіть замовлення ще раз. "
                    "Оплати не відбулося.",
                    "redirect_url": await self.get_success_url(
                        region_slug, data["selected_currency"]
                    ),
                    "redirect_message": "У корзину",
                },
                status=400,
            )

        order_number = f"{region_slug}-{str(uuid4())[:6]}"
        created_order_json = await order_handlers.create_order(
            cart_products, order_number, region_slug, selected_currency, data
        )
        if created_order_json["data"][0]["status"] == "success":
            order_id = created_order_json["data"][0]["details"]["id"]
            await session_data.remove_ordered_products(session, cart_products_ids)
            await session_data.add_order(session, order_id)
            # await self.notify_user_by_email_or_sms(
            #     data["customer_phone_number"],
            #     order_number,
            #     created_order_json["data"][0]["grand_total"],
            #     selected_currency,
            #     data["customer_email"],
            # )
            return render(
                self.request,
                "templates/notification.html",
                {
                    "title": "BonnyFlowers",
                    "header": "Замовлення створено!",
                    "message_top": "Номер замовлення - ",
                    "spanned_message": order_number,
                    "message_bottom": "Списання відбудеться протягом 3-ох днів",
                    "redirect_url": await self.get_success_url(
                        region_slug, data["selected_currency"]
                    ),
                    "redirect_message": "У кошик",
                },
                status=201,
            )
        return HttpResponseRedirect(
            await self.get_success_url(region_slug, data["selected_currency"])
        )

    @staticmethod
    async def notify_user_by_email_or_sms(
        customer_phone_number: str,
        order_number: str,
        order_grand_total: int,
        order_currency: dict[str, Any],
        customer_email: str | None = None,
    ):
        """
        Notify the user about a successful order payment via email or SMS.

        Args:
            customer_phone_number (str): The customer's phone number for SMS notification.
            order_number (str): The unique identifier for the order.
            order_grand_total (int): The total amount paid for the order.
            order_currency (dict[str, Any]): A dictionary containing information about the order currency.
            customer_email (str | None, optional): The customer's email address for email notification. Defaults to None.

        Returns:
            None
        """
        client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN"),
            http_client=AsyncTwilioHttpClient(pool_connections=False),
        )
        await client.messages.create_async(
            to=customer_phone_number,
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            body=f"Приветствуем! Вы успешно оплатили заказ {order_number} на сумму {order_grand_total}{order_currency.get('symbol')} на BonnyFlowers.",
        )

        if customer_email:
            send_mail(
                f"Подтверждение заказа {order_number} в BonnyFlowers",
                f"Приветствуем! Вы успешно оплатили заказ {order_number} на сумму {order_grand_total}{order_currency.get('symbol')} на BonnyFlowers..",
                recipient_list=[
                    customer_email,
                ],
                from_email=None,
            )

    async def form_invalid(self, form: AsyncForm) -> TemplateResponse:
        """Test."""
        return await super().form_invalid(form)

    async def get_success_url(self, region_slug: str, selected_currency: str) -> str:
        """Test."""
        return (
            reverse_lazy("cart:cart", kwargs={"region_slug": region_slug})
            + f"?currency={selected_currency}"
        )


class OrdersList(AsyncTemplateView, ApplicationMixin):
    """To represent list of customer orders."""

    template_name = "orders/ordersList.html"

    class OrderStatus(Enum):
        pending: str = "В ожидании"
        in_progress: str = "В работе"
        return_: str = "Возврат"
        delivered: str = "Доставлено"

    async def get_context_data(self, *args, **kwargs):
        """
        Retrieve and return the context data for rendering the orders list page.

        Args:
            *args: Variable-length arguments.
            **kwargs: Keyword arguments.

        Returns:
            dict: A dictionary containing the context data.
        """
        context = await self.get_common_context(
            **await super().get_context_data(*args, **kwargs)
        )
        if isinstance(context, HttpResponseServerError):
            return context
        client_orders_id_list = await session_data.get_client_orders_id_list(
            self.request.session
        )
        fetched_orders = await order_handlers.get_client_orders(client_orders_id_list)
        context["orders"] = []
        currencies = await crm_data.get_currency_list(self.request)
        for order in fetched_orders:
            try:
                context["orders"].append(
                    {
                        "number": order["data"][0]["order_number"],
                        "target_delivery_date": order["data"][0]["target_delivery_date"],
                        "grand_total": order["data"][0]["grand_total"],
                        "status": self.OrderStatus(order["data"][0]["order_status"]),
                        "products": [
                            {
                                "sku": product["sku"],
                                "name": product["product_id"]["name"],
                                "amount": product["amount"],
                                "price": product["price"],
                            }
                            for product in order["data"][0]["ordered_products"]
                        ],
                        "selected_currency": next(
                            currency
                            for currency in currencies
                            if currency["id"] == order["data"][0]["order_currency_id"]["id"]
                        ),
                    }
                )
            except ValueError:
                return HttpResponseServerError(
                    render(
                        self.request,
                        "templates/notification.html",
                        {
                            "header": "Server error",
                            "message_top": "We are so sorry, but the shop isn't \
                            initialized properly (wrong orders status)",
                            "message_bottom": "You can notify an owner about it",
                            "redirect_link": (
                                reverse_lazy(
                                    "cart:cart", kwargs={"region_slug": context["region_slug"]}
                                )
                                + "?currency="
                                + context.get("selected_currency")["Name"]
                            ),
                            "redirect_message": "Repeat",
                        },
                    ),
                    status=503,
                )
        context["orders_statutes"] = {
            "pending": self.OrderStatus.pending.value,
            "return": self.OrderStatus.return_.value,
            "in_progress": self.OrderStatus.in_progress.value,
            "delivered": self.OrderStatus.delivered.value,
        }
        return context
