from django.urls import  path

from api.appointment.views import AppointmentViewset, PatientAppointmentViewset, PrescriptionViewset, TreatmentViewset

trailing_slash = False

urlpatterns = [    
    path('appointment', AppointmentViewset.as_view({'post': 'create', 'get': 'list'}), name='appointment'),
    path('appointment/<uuid:pk>', AppointmentViewset.as_view({'get': 'retrieve', 'patch': 'partial_update'}), name='appointment-list'),
    path('appointment/patient-detail', AppointmentViewset.as_view({'post': 'add_patient_details'}), name='appointment-patient-detail'),
    path('appointment/patient-detail/<uuid:appointment_id>', AppointmentViewset.as_view({'get': 'get_patient_details'}), name='appointment-patient-detail'),
    
    path('appointment-table/<str:date_range>', AppointmentViewset.as_view({'get': 'list'}), name='appointment_table'),
    
    path('prescription', PrescriptionViewset.as_view({'post': 'create', 'get': 'list'}), name='prescription'),
    path('prescription/<uuid:pk>', PrescriptionViewset.as_view({'get': 'retrieve', 'patch': 'partial_update'}), name='prescription-list'),
    path('prescription/item/<uuid:appointment_id>', PrescriptionViewset.as_view({'get': 'get_prescription_item'}), name='prescription-items'),
    path('prescription/item-stock/<uuid:prescription_id>', PrescriptionViewset.as_view({'get': 'get_prescription_item_and_stock'}), name='prescription-items-stock'),    
    path('prescription-table/<str:date_range>', PrescriptionViewset.as_view({'get': 'list'}), name='prescription'),
    
    path('patient-appointment', PatientAppointmentViewset.as_view({'get': 'get_appointment_list'}), name='patient-appointment'),
    path('patient-treatment', PatientAppointmentViewset.as_view({'get': 'get_patient_treatment'}), name='patient-treatment'),
    
    
    path('appointment/treatment-before-images', AppointmentViewset.as_view({'post': 'upload_treatment_before_image'}), name='treatment-before-images'),
    path('appointment/treatment-after-images', AppointmentViewset.as_view({'post': 'upload_treatment_after_image'}), name='treatment-after-images'),
    
    
    path('appointment/treatment/<uuid:pk>', TreatmentViewset.as_view({'get': 'retrieve', 'patch': 'partial_update'}), name='treatment'),


]