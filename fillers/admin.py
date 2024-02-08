from django.contrib import admin
from .models import AboutUsContextModel, DeliveryDataModel, ContactsDataModel

# Register your models here.
admin.site.register(AboutUsContextModel)
admin.site.register(DeliveryDataModel)
admin.site.register(ContactsDataModel)
