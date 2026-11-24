from django.contrib import admin
from api.core.models import BranchUser, Disease, Patient, StateMaster, CityMaster, Branch, SubDisease,UserRole, Vendor, TreatmentTestsMaster    

admin.site.register(StateMaster)
admin.site.register(CityMaster)
admin.site.register(Branch)
admin.site.register(UserRole)
admin.site.register(BranchUser)
admin.site.register(Patient)
admin.site.register(Disease)
admin.site.register(SubDisease)
admin.site.register(Vendor)
admin.site.register(TreatmentTestsMaster)