import time
from django.shortcuts import render
from api.account.utils import delete_google_calendar_event, get_date_range_by_entity
from django.conf import settings

from api.appointment.models import Appointment, AppointmentPatientAfterTreatmentImages, AppointmentPatientImages, AppointmentTreatment, GoogleCalendarAppointment, Prescription, PrescriptionItem, PrescriptionTestsAdvised

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response

from api.appointment.serializers import AdviceTestItemSerializer, AppointmentDetailsSerializer, AppointmentPatientAfterImageSerializer, AppointmentPatientImageSerializer, AppointmentPrescriptionSerializer, AppointmentSerializer, AppointmentTreatmentDetailSerializer, AppointmentTreatmentImageSerializer, AppointmentTreatmentSerializer, CalendarAppointmentSerializer, PrescriptionItemSerializer, PrescriptionItemWithStockSerializer, PrescriptionSerializer, TreatmentSerializer

from rest_framework.decorators import action

from api.inventory.models import Purchase, PurchaseItem, SalesItem
from rest_framework.decorators import action
from rest_framework import filters

from django.db.models import F, Sum
from rest_framework import pagination

from api.core.models import BranchUser



class AppointmentViewset(viewsets.ModelViewSet):
    queryset = Appointment.objects.order_by("-created_at")
    serializer_class = AppointmentSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['patient__name', 'doctor__name', 'status']
        
    def list(self, request, *args, **kwargs):           
        self.serializer_class = AppointmentPrescriptionSerializer
        if request.GET.get("for") == "calendar":
            self.pagination_class = None
            self.serializer_class = CalendarAppointmentSerializer
            self.queryset = self.get_queryset().select_related("patient", "doctor", "branch")
        

        user_branch_list = BranchUser.objects.filter(user_id = request.user.id).values_list('branch', flat=True)

        if request.GET.get("branch_id"):
            self.queryset = self.get_queryset().filter(branch_id=request.GET.get("branch_id"))
        else:
            self.queryset = self.get_queryset().filter(branch_id__in=user_branch_list)
        
            
        if request.GET.get("doctor_id"):
            self.queryset = self.get_queryset().filter(doctor_id=request.GET.get("doctor_id"))
        
        if kwargs.get("date_range"): 
            
            pagination.PageNumberPagination.page_size = request.GET.get('count_per_page', 10)
            if not request.GET.get("paginate"):
                self.pagination_class = None
            
            date_data = get_date_range_by_entity(kwargs.get("date_range"))
            if date_data:
                start_date = date_data.get("start_date")
                end_date = date_data.get("end_date")
                self.queryset = self.get_queryset().filter(appointment_at__gte=start_date, appointment_at__lte=end_date)    
            
        response = super().list(request, *args, **kwargs)
        return Response(status=response.status_code, data={'status': 'SUCCESS', 'data': response.data })
    
    
    def create(self, request, *args, **kwargs):
        # request.data._mutable = True
        print("==== Start ====")
        response = super().create(request, *args, **kwargs)              
        return Response(status=response.status_code, data={'status': 'SUCCESS', 'data': response.data })
    
    
    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        if response.status_code == 200 and not getattr(settings, "LOCAL_OFFLINE", False):
            appointment_id = response.data['id']
            if response.data['status'] == "Cancelled":
                try:
                    event_list = GoogleCalendarAppointment.objects.filter(appointment_id=appointment_id)
                    if event_list:
                        event_id = event_list[0].google_calendar_event_id
                        delete_google_calendar_event(event_id)
                except:
                    print("Already delete from google calendar")
                
        return response
        
    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = AppointmentDetailsSerializer 
        response = super().retrieve(request, *args, **kwargs)
        return Response(status=response.status_code, data={'status': 'SUCCESS', 'data': response.data })
    
    
    @action(detail=False,methods=['POST'])
    def upload_treatment_before_image(self, request, *args, **kwargs):
        data = []
        
        treatment_id = request.data.get("treatment_id")
        appointment_id = request.data.get("appointment_id")
        is_delete = request.data.get("action")
        
        if is_delete == "yes":
            img_obj = AppointmentPatientImages.objects.filter(appointment_id=appointment_id)
            if img_obj:
                img_obj.delete()
        
        image_list = []
        for file in request.FILES.getlist("images"):
            image_list.append({
                'appointment_treatment': treatment_id, 
                'image': file, 
                'appointment': appointment_id
            })
            
        img_serializer_obj = AppointmentPatientImageSerializer(data=image_list, many=True)
        if img_serializer_obj.is_valid():
            img_serializer_obj.save()
            data = img_serializer_obj.data
        else:
            print("Image Serializer == ", img_serializer_obj.errors)
                
        return Response(status=200, data={'status': 'SUCCESS', 'data': data})
    
    
    @action(detail=False,methods=['POST'])
    def upload_treatment_after_image(self, request, *args, **kwargs):
        data = []

        
        treatment_id = request.data.get("treatment_id")
        appointment_id = request.data.get("appointment_id")
        is_delete = request.data.get("action")
        
        if is_delete == "yes":
            img_obj = AppointmentPatientAfterTreatmentImages.objects.filter(appointment_id=appointment_id)
            if img_obj:
                img_obj.delete()
            
        after_image_list = []
        for file in request.FILES.getlist("images"):
            after_image_list.append({
                'appointment_treatment': treatment_id, 
                'image': file, 
                'appointment': appointment_id
            })
            
        img_serializer_obj = AppointmentPatientAfterImageSerializer(data=after_image_list, many=True)
        if img_serializer_obj.is_valid():
            img_serializer_obj.save()
            data = img_serializer_obj.data
        else:
            print("Image Serializer == ", img_serializer_obj.errors)
                
        return Response(status=200, data={'status': 'SUCCESS', 'data': data})
    
    
    @action(detail=False,methods=['POST'])
    def add_patient_details(self, request, *args, **kwargs):
        data = []
        serializer_obj = AppointmentTreatmentSerializer(data=request.data)
        if serializer_obj.is_valid():
            serializer_obj.save()
            
            
            treatment_obj = AppointmentTreatment.objects.filter(id=serializer_obj.data['id'])            
            
            try:
                # Update sub disease list
                sub_disease_list = request.data.getlist("sub_disease")
                for sd in sub_disease_list:
                    treatment_obj.sub_disease.add(sd)
            except:
                pass
                
            # data.append(serializer_obj.data)
            # data[0]['images'] = []
            # data[0]['after_images'] = []
            
            image_list = []
            for file in request.FILES.getlist("files"):
                image_list.append({
                   'appointment_treatment': serializer_obj.data['id'], 
                   'image': file, 
                   'appointment': request.data.get('appointment')
                })
                
            img_serializer_obj = AppointmentPatientImageSerializer(data=image_list, many=True)
            if img_serializer_obj.is_valid():
                img_serializer_obj.save()
                # data[0]['images'] = img_serializer_obj.data
            else:
                print("Image Serializer == ", img_serializer_obj.errors)
                
            
            # Save After Images
            after_image_list = []
            for file in request.FILES.getlist("after_files"):
                after_image_list.append({
                   'appointment_treatment': serializer_obj.data['id'], 
                   'image': file, 
                   'appointment': request.data.get('appointment')
                })
                
            img_serializer_obj = AppointmentPatientAfterImageSerializer(data=after_image_list, many=True)
            if img_serializer_obj.is_valid():
                img_serializer_obj.save()
                # data[0]['after_images'] = img_serializer_obj.data
            else:
                print("Image Serializer == ", img_serializer_obj.errors)
                
            treatment_list = AppointmentTreatmentDetailSerializer(treatment_obj, many=True).data
            data.append(treatment_list[0])
        else:
            print("Treatment Errors ", serializer_obj.errors)
            
        
        return Response(status=200, data={'status': 'SUCCESS', 'data': data})
    
    
    @action(detail=True,methods=['GET'])
    def get_patient_details(self, request, *args, **kwargs):
        appointment_id = kwargs.get('appointment_id')
        treatment_obj = AppointmentTreatment.objects.filter(appointment_id=appointment_id)
        treatment_list = AppointmentTreatmentDetailSerializer(treatment_obj, many=True).data
        return Response(status=200, data={'status': 'SUCCESS', 'data': treatment_list})
        
        
        
class PrescriptionViewset(viewsets.ModelViewSet):
    queryset = Prescription.objects.select_related("appointment", "patient", "doctor", "branch").order_by("-created_at")
    serializer_class = PrescriptionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['patient__name', 'patient__email', 'patient__mobile', 'doctor__name', 'doctor__email', 'doctor__mobile']
    
    def list(self, request, *args, **kwargs):        
        if not request.GET.get("paginate"):
            self.pagination_class = None
            
            
        if kwargs.get("date_range"):    
            date_data = get_date_range_by_entity(kwargs.get("date_range"))
            if date_data:
                start_date = date_data.get("start_date")
                end_date = date_data.get("end_date")
                self.queryset = self.get_queryset().filter(created_at__gte=start_date, created_at__lte=end_date)    
            
            
        response = super().list(request, *args, **kwargs)
        return Response(status=response.status_code, data={'status': 'SUCCESS', 'data': response.data })
    
    def create(self, request, *args, **kwargs):
        # Delete Before Insert
        prescription_obj = Prescription.objects.filter(appointment_id=request.data.get('appointment'))
        if prescription_obj:
            item_list = PrescriptionItem.objects.filter(prescription__appointment_id=request.data.get('appointment'))
            advice_test_list = PrescriptionTestsAdvised.objects.filter(prescription__appointment_id=request.data.get('appointment'))
            
            item_list.delete()
            advice_test_list.delete()
            prescription_obj.delete()
            
        # Create new Prescription
        prescription_items = request.data.get('items')        
        advice_test_list = request.data.get('advice_test_list')   
             
        response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:   
            # Medicine Section
            for item in prescription_items:
                item['prescription'] = response.data['id']
                                
            serializer_obj = PrescriptionItemSerializer(data=prescription_items, many=True)
            if serializer_obj.is_valid():
                serializer_obj.save()
                print("Save Called")
            else:
                print("Serializer Errors == ", serializer_obj.errors)
                
            
            try:
                # Advice Test Section 
                for item in advice_test_list:
                    item['prescription'] = response.data['id']
                    item['adviced_test'] = item['advice_test_id']
                    
                                    
                serializer_obj = AdviceTestItemSerializer(data=advice_test_list, many=True)
                if serializer_obj.is_valid():
                    serializer_obj.save()
                else:
                    print("Serializer Errors == ", serializer_obj.errors)
            except:
                pass    
        
        prescription_items1 = PrescriptionItem.objects.filter(prescription__appointment_id=response.data['appointment']['id']).order_by('-created_at')
        data = PrescriptionItemSerializer(prescription_items1, many=True).data
        
        try:
            advice_test_list_1 = PrescriptionTestsAdvised.objects.filter(prescription__appointment_id=response.data['appointment']['id']).order_by('-created_at')
            data_advice = AdviceTestItemSerializer(advice_test_list_1, many=True).data
        except:
            data_advice = []
        
        return Response(status=status.HTTP_201_CREATED, data={'status': 'SUCCESS', 'data_advice':data_advice, 'data': data, 'error': serializer_obj.errors, 'prescription_items': prescription_items })
    
    
    @action(detail=False,methods=['GET'])
    def get_prescription_item(self, request, *args, **kwargs):
        appointment_id = kwargs.get('appointment_id') 
        prescription_items = PrescriptionItem.objects.filter(prescription__appointment_id=appointment_id).order_by('-created_at')
        data = PrescriptionItemSerializer(prescription_items, many=True).data
        
        advice_test_list_1 = PrescriptionTestsAdvised.objects.filter(prescription__appointment_id=appointment_id).order_by('-created_at')
        data_advice = AdviceTestItemSerializer(advice_test_list_1, many=True).data
        
        
        return Response(status=status.HTTP_200_OK, data={'status': 'SUCCESS', 'data': data,'data_advice':data_advice }) 
    
    
    @action(detail=False,methods=['GET'])
    def get_prescription_item_and_stock(self, request, *args, **kwargs):
        prescription_id = kwargs.get('prescription_id') 
        prescription_items = PrescriptionItem.objects.filter(prescription_id=prescription_id)
        data = PrescriptionItemWithStockSerializer(prescription_items, many=True).data
        return Response(status=status.HTTP_200_OK, data={'status': 'SUCCESS', 'data': data }) 
    
    
        
class PatientAppointmentViewset(viewsets.ViewSet):
    
    @action (detail=True)
    def get_appointment_list(self, request, *args, **kwargs):
        patient_id = request.GET.get('patient_id')
        appointment_list = Appointment.objects.select_related("patient").select_related("doctor").prefetch_related(
                "prescription_appointment").values(
                'doctor__name', 'patient__name', 'status', 'appointment_at', "id", "patient",
                'visited_at', 'cancelled_at', 'prescription_appointment__id'
            ).filter(patient_id=patient_id )
        return Response(status=status.HTTP_200_OK, data={'status': 'SUCCESS', 'data': appointment_list })
        
    @action (detail=True)
    def get_patient_treatment(self, request, *args, **kwargs):
        patient_id = request.GET.get('patient_id')
        appointment_id = request.GET.get('appointment_id')
        
        treatment_list = AppointmentTreatment.objects.select_related("sub_disease").values(
                'sub_disease__name', "observation"
            ).filter(patient_id=patient_id, appointment_id=appointment_id)
    
        image_list = AppointmentPatientImages.objects.filter(appointment_id=appointment_id)
        
        prescription_items = PrescriptionItem.objects.select_related("medicine").values(
            'dose', 'frequency','duration_count', 'duration_name', 'instruction', 'medicine__name'
        ).filter(prescription__appointment_id=appointment_id)
            
        data = {
            'images': AppointmentTreatmentImageSerializer(image_list, many=True).data,
            'treatment': treatment_list,
            'prescription_item': prescription_items
        }
        
        return Response(status=status.HTTP_200_OK, data={'status': 'SUCCESS', 'data': data })
    
    
    
class TreatmentViewset(viewsets.ModelViewSet):
    queryset = AppointmentTreatment.objects.order_by("-created_at")
    serializer_class = TreatmentSerializer
    
    def patch(self, request, *args, **kwargs):
        response = super().patch(request, *args, **kwargs)              
        return Response(status=response.status_code, data={'status': 'SUCCESS', 'data': response.data })


# https://stackoverflow.com/questions/65419603/how-to-display-multiple-selected-values-from-a-dropdown-in-react


# <option value="">Select Treatment</option><option value="4ac6f7b0-8b76-4700-a1ac-c10b5307a587">Test Diseasee model edit 2</option><option value="047d5414-ed17-4c85-a877-85f7ab83760a">Test Diseasee model</option><option value="64dbc96a-b452-4a87-9b37-57e45e33c14d">bdbd1</option><option value="e2f2687b-5558-43d8-ad0a-2a78650199fd">test 4</option><option value="4d732bec-53ba-47ae-a4c7-b57b638ebcb3">Test 3</option><option value="b0c62de4-6dd3-4bce-9a2e-0fe692791a41">Test</option><option value="0dc1d09e-5b84-4aa1-8fd7-2367bdc5c3e4">Test Disease 1</option><option value="">Select Treatment</option><option value="4ac6f7b0-8b76-4700-a1ac-c10b5307a587">Test Diseasee model edit 2</option><option value="047d5414-ed17-4c85-a877-85f7ab83760a">Test Diseasee model</option><option value="64dbc96a-b452-4a87-9b37-57e45e33c14d">bdbd1</option><option value="e2f2687b-5558-43d8-ad0a-2a78650199fd">test 4</option><option value="4d732bec-53ba-47ae-a4c7-b57b638ebcb3">Test 3</option><option value="b0c62de4-6dd3-4bce-9a2e-0fe692791a41">Test</option><option value="0dc1d09e-5b84-4aa1-8fd7-2367bdc5c3e4">Test Disease 1</option>



