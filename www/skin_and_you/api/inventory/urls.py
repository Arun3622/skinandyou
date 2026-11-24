from django.urls import  path
from api.core.views import PatientViewset, RoleViewset, StateViewset, CityViewset, BranchViewset,DiseaseViewset,SubDiseaseViewset
from api.inventory.models import Medicine, MedicineCategory
from api.inventory.views import MedicineCategroyViewset, MedicineViewset, PurchaseViewset, SalesViewset

urlpatterns = [    

    path('medicine', MedicineViewset.as_view({'get': 'list', 'post': 'create'}), name='medicine'),
    path('medicine/<uuid:pk>', MedicineViewset.as_view({'patch': 'partial_update', 'get': 'retrieve',}), name='medicine'),
    
    path('medicine-category', MedicineViewset.as_view({'get': 'category_list', 'post': 'category_add'}), name='medicine-category'),

    path('purchase', PurchaseViewset.as_view({'get': 'list', 'post': 'create'}), name='purchase'),
    path('purchase/<uuid:pk>', PurchaseViewset.as_view({'get': 'retrieve', 'patch': 'partial_update'}), name='purchase'),

    path('sales', SalesViewset.as_view({'get': 'list', 'post': 'create'}), name='sales'),
    path('sales/<uuid:pk>', SalesViewset.as_view({'get': 'retrieve', 'patch': 'partial_update'}), name='sales'),
    
    
    path('medicine/category', MedicineCategroyViewset.as_view({'get': 'list', 'post': 'create'}), name='medicine_category'),
    path('medicine/category/<uuid:pk>', MedicineCategroyViewset.as_view({'get': 'retrieve', 'patch': 'partial_update'}), name='medicine_category'),
    

    
    # path('branch', BranchViewset.as_view({'post': 'create', 'get': 'list',}), name='branch'),
    # path('branch/<uuid:pk>', BranchViewset.as_view({'patch': 'partial_update', 'get': 'retrieve',}), name='branch'),
    
    # path('disease', DiseaseViewset.as_view({'post': 'create', 'get': 'list',}), name='disease'),
    # path('disease/<uuid:pk>', DiseaseViewset.as_view({'patch': 'partial_update', 'get': 'retrieve',}), name='disease'),
    
    # path('sub-disease', SubDiseaseViewset.as_view({'post': 'create', 'get': 'list',}), name='branch'),
    # path('sub-disease/<uuid:pk>', SubDiseaseViewset.as_view({'patch': 'partial_update', 'get': 'retrieve',}), name='sub-disease'),
    
    # path('role', RoleViewset.as_view({'post': 'create', 'get': 'list',}), name='role'),
    
    # path('patient', PatientViewset.as_view({'get': 'list',}), name='patient-list'),
]