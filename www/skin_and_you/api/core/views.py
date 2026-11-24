from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.views import APIView
from api.account.models import User
from api.account.serializers import UserSerializer
from api.core.models import  BranchUser, Branch, Patient, StateMaster, CityMaster, Disease, SubDisease, TreatmentTestsMaster, UserRole, Vendor
from api.core.serializers import BranchDetailSerializer, BranchSerializer, CitySerializer, DiseaseSerializer,  PatientSerializer, RoleSerializer, StateSerializer, SubDiseaseSerializer, TreatmentTestAdviceSerializer, VendorSerializer
from rest_framework.response import Response

# from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import pagination





class StateViewset(viewsets.ModelViewSet):
    queryset = StateMaster.objects.all()
    serializer_class = StateSerializer
    pagination_class = None
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response(status=response.status_code, data={'status': 'SUCCESS', 'data': response.data }) 
        

class CityViewset(viewsets.ModelViewSet):
    queryset = CityMaster.objects.all()
    serializer_class = CitySerializer
    pagination_class = None
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response(status=response.status_code, data={'status': 'SUCCESS', 'data': response.data })
    

class BranchViewset(viewsets.ModelViewSet):
    queryset = Branch.objects.all().order_by("-created_at")
    serializer_class = BranchSerializer
    pagination_class = None
    # permission_classes = [AllowAny]
    
    def list(self, request, *args, **kwargs):
        
        from api.core.models import BranchUser
        user_branch_list = BranchUser.objects.filter(user_id = request.user.id).values_list('branch', flat=True)
        if request.GET.get("branch_id"):
            self.queryset = self.get_queryset().filter(id=request.GET.get("branch_id"))
        else:
            self.queryset = self.get_queryset().filter(id__in=user_branch_list)


        if request.GET.get("records") == "all":
            response = super().list(request, *args, **kwargs)
            return Response(status=response.status_code, data={'status': 'SUCCESS', 'data': response.data })
    
        return super().list(request, *args, **kwargs)
    
    
    def create(self, request, *args, **kwargs):
        request.data._mutable = True
        return super().create(request, *args, **kwargs)
    
    
    def patch(self, request, *args, **kwargs):
        request.data._mutable = True
        return super().patch(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        if request.GET.get("convert") == "fk":
            self.serializer_class = BranchDetailSerializer
        # request.data._mutable = True
        response = super().retrieve(request, *args, **kwargs)
        return Response(status=response.status_code, data={'status': 'SUCCESS', 'data': response.data })
    
    
    
    # def delete(self, request, *args, **kwargs):
    #     request.data._mutable = True
    #     return super().patch(request, *args, **kwargs)
    
    
    
class DiseaseViewset(viewsets.ModelViewSet):
    queryset = Disease.objects.all()
    serializer_class = DiseaseSerializer
    pagination_class = None
    # permission_classes = [AllowAny]
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response(status=response.status_code, data={'status': 'SUCCESS', 'data': response.data })
    
    
    def create(self, request, *args, **kwargs):
        request.data._mutable = True
        return super().create(request, *args, **kwargs)
    
    
    def patch(self, request, *args, **kwargs):
        request.data._mutable = True
        return super().patch(request, *args, **kwargs)
    
    
    def delete(self, request, *args, **kwargs):
        request.data._mutable = True
        return super().patch(request, *args, **kwargs)
    
    
class SubDiseaseViewset(viewsets.ModelViewSet):
    queryset = SubDisease.objects.all().order_by("-created_at")
    serializer_class = SubDiseaseSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'disease_for']
    
    
    def list(self, request, *args, **kwargs):
        if not request.GET.get("paginate"):
            self.pagination_class = None
            
        response = super().list(request, *args, **kwargs)
        return Response(status=response.status_code, data={'status': 'SUCCESS', 'data': response.data })
    
    
    def create(self, request, *args, **kwargs):
        request.data._mutable = True
        return super().create(request, *args, **kwargs)
    
    
    def patch(self, request, *args, **kwargs):
        request.data._mutable = True
        return super().patch(request, *args, **kwargs)
    
    
    def delete(self, request, *args, **kwargs):
        request.data._mutable = True
        return super().patch(request, *args, **kwargs)
    
    
class RoleViewset(viewsets.ModelViewSet):
    queryset = UserRole.objects.all()
    serializer_class = RoleSerializer
    pagination_class = None
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response(status=response.status_code, data={'status': 'SUCCESS', 'data': response.data })
    
    
class PatientViewset(viewsets.ModelViewSet):
    queryset = Patient.objects.select_related("user")
    serializer_class = PatientSerializer
    pagination_class = None
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__email', 'user__name', 'user__mobile', 'user__id']
    
    def list(self, request, *args, **kwargs):
        user_branch_list = BranchUser.objects.filter(user_id = request.user.id).values_list('branch', flat=True)
        self.queryset = self.get_queryset().filter(branch_id__in=user_branch_list)


        if not request.GET.get("search"):
            data = Patient.objects.select_related("user").filter(branch_id__in=user_branch_list).values("user__id", "user__name")
            return Response(status=200, data={'status': 'SUCCESS', 'data': data }) 
            
        response = super().list(request, *args, **kwargs)
        return Response(status=response.status_code, data={'status': 'SUCCESS', 'data': response.data }) 
    
    
    
class VendorViewset(viewsets.ModelViewSet):
    queryset = Vendor.objects.filter(is_active=True).order_by("-created_at")
    serializer_class = VendorSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'email', 'contact']

    
    def list(self, request, *args, **kwargs):    
        pagination.PageNumberPagination.page_size = request.GET.get('count_per_page', 10)
   
        if not request.GET.get("paginate"):
            self.pagination_class = None   
            
        response = super().list(request, *args, **kwargs)
        return Response(status=response.status_code, data={'status': 'SUCCESS', 'data': response.data })

    
    def create(self, request, *args, **kwargs):
        request.data._mutable = True
        request.data['created_by'] = request.user.id
        response = super().create(request, *args, **kwargs)              
        return Response(status=response.status_code, data={'status': 'SUCCESS', 'data': response.data })
    
    def partial_update(self, request, *args, **kwargs):
        request.data._mutable = True
        request.data['updated_by'] = request.user.id
        response = super().partial_update(request, *args, **kwargs)              
        return Response(status=response.status_code, data={'status': 'SUCCESS', 'data': response.data })
    
    def retrieve(self, request, *args, **kwargs):       
        response = super().retrieve(request, *args, **kwargs)
        return Response(status=response.status_code, data={'status': 'SUCCESS', 'data': response.data })
    
    
    
class TreatmentTestAdviceMasterViewset(viewsets.ModelViewSet):
    queryset = TreatmentTestsMaster.objects.all()
    serializer_class = TreatmentTestAdviceSerializer
    pagination_class = None
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response(status=response.status_code, data={'status': 'SUCCESS', 'data': response.data })
    