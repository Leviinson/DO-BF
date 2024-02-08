"""Function and class views list for 'zoho_token' app."""
from django.http import HttpResponse


def test_view(request):
    return HttpResponse("Тест")
