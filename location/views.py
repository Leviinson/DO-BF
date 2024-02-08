"""Feedback views."""
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy

from async_views.generic.edit import AsyncFormView
from services.data_getters import crm_data

from .forms import AsyncLocationForm


# Create your views here.
class LocationView(AsyncFormView):
    """Individual order endpoint controller."""

    form_class = AsyncLocationForm
    http_method_names = [
        "get",
    ]

    async def get(self, request: HttpRequest):
        """
        To create a feedback record in Zoho CRM.

        Args:
            request (HttpRequest): The client's request.

        Returns:
            JsonResponse: JSON response to the request.
        """
        form = AsyncLocationForm(request.GET)
        if await form.async_is_valid():
            data: dict[str, str | int] = form.cleaned_data
            if not data.get("country") or not data.get("city"):
                return JsonResponse({"msg": "Wrong data passed"}, status=400)
            regions = await crm_data.get_regions_list(self.request)
            for region in regions:
                if region["code"].lower() == data["city"].lower():
                    return HttpResponseRedirect(
                        reverse_lazy(
                            "main_page:mainpage-view", kwargs={"region_slug": region["slug"]}
                        )
                    )
        return HttpResponseRedirect(reverse_lazy("main_page:main_page"))
