"""Feedback views."""
import json
from typing import Dict, Union

from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect

from services.crm_interface import custom_record_operations


# Create your views here.
@method_decorator(csrf_protect, name="dispatch")
class FeedbackView(View):
    """Individual order endpoint controller."""

    http_method_names = [
        "post",
    ]

    async def post(self, request: HttpRequest):
        """
        To create a feedback record in Zoho CRM.

        Args:
            request (HttpRequest): The client's request.

        Returns:
            JsonResponse: JSON response to the request.
        """
        try:
            data: Dict[str, Union[str, int]] = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"msg": "Wrong data passed"}, status=400)
        if (phone_number := data.get("full_number")) and (name := data.get("name")):
            data = {}

            # if (user := request.user).is_authenticated:
            #     record = Record()
            #     record.set_id(user.zoho_id)
            #     data["customer_id"] = record

            data["customer_phone_number"] = phone_number
            data["customer_name"] = name
            feedback_record = await custom_record_operations.create_records(
                module_api_name="callbacks",
                data=[
                    data,
                ],
            )
            if not feedback_record:
                return JsonResponse({"msg": "Неожиданная проблема"}, status=500)
            return JsonResponse({}, status=201)
        return JsonResponse({"msg": "Не все поля заполнены."}, status=400)
