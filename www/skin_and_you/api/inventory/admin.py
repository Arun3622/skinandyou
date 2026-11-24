from django.contrib import admin

from api.inventory.models import Medicine, MedicineCategory, MedicineForDisease, MedicineQty, Purchase, PurchaseItem, Sales, SalesItem


admin.site.register(MedicineCategory)
admin.site.register(Medicine)
admin.site.register(MedicineQty)
admin.site.register(MedicineForDisease)

admin.site.register(Purchase)
admin.site.register(PurchaseItem)
admin.site.register(Sales)
admin.site.register(SalesItem)