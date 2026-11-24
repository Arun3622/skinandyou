from django.urls import  path
from api.core.views import PatientViewset, RoleViewset, StateViewset, CityViewset, BranchViewset,DiseaseViewset,SubDiseaseViewset, TreatmentTestAdviceMasterViewset, VendorViewset

urlpatterns = [    

    path('state', StateViewset.as_view({'get': 'list'}), name='state'),
    path('city', CityViewset.as_view({'get': 'list'}), name='city'),
    
    path('branch', BranchViewset.as_view({'post': 'create', 'get': 'list',}), name='branch'),
    path('branch/<uuid:pk>', BranchViewset.as_view({'patch': 'partial_update', 'get': 'retrieve',}), name='branch'),
    
    path('disease', DiseaseViewset.as_view({'post': 'create', 'get': 'list',}), name='disease'),
    path('disease/<uuid:pk>', DiseaseViewset.as_view({'patch': 'partial_update', 'get': 'retrieve',}), name='disease'),
    
    path('sub-disease', SubDiseaseViewset.as_view({'post': 'create', 'get': 'list',}), name='branch'),
    path('sub-disease/<uuid:pk>', SubDiseaseViewset.as_view({'patch': 'partial_update', 'get': 'retrieve',}), name='sub-disease'),
    
    path('role', RoleViewset.as_view({'post': 'create', 'get': 'list',}), name='role'),
    
    path('patient', PatientViewset.as_view({'get': 'list',}), name='patient-list'),
    
    
    path('vendor', VendorViewset.as_view({'post': 'create', 'get': 'list',}), name='vendor'),
    path('vendor/<uuid:pk>', VendorViewset.as_view({'patch': 'partial_update', 'get': 'retrieve',}), name='vendor'),
    
    path('treatment-test-master', TreatmentTestAdviceMasterViewset.as_view({'post': 'create', 'get': 'list',}), name='treatment-test-master'),
    path('treatment-test-master/<uuid:pk>', TreatmentTestAdviceMasterViewset.as_view({'patch': 'partial_update', 'get': 'retrieve',}), name='treatment-test-master'),
    
]