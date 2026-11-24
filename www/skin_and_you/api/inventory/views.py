import json
from rest_framework import viewsets, status
from rest_framework.views import APIView
from api.account.serializers import UserSerializer
from rest_framework.response import Response
from api.account.utils import delete_google_calendar_event
from api.core.models import Branch

from api.inventory.models import Medicine, MedicineCategory, MedicineQty, Purchase, Sales
from api.inventory.serializers import MedicineCategorySerializer, MedicineSerializer, PurchaseDetailSerializer, PurchaseItemSerializer, PurchaseSerializer, PurchaseWithItemSerializer, SalesItemSerializer, SalesSerializer

from rest_framework.decorators import action
from rest_framework import filters
from rest_framework import pagination



class MedicineViewset(viewsets.ModelViewSet):
    queryset = Medicine.objects.select_related("medicine_category")
    serializer_class = MedicineSerializer
    # pagination_class = True
    
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'content','sku_code','sku_code','total_qty', 'medicine_category__name']
   
    
    
    def list(self, request, *args, **kwargs):      
        self.serializer_class.context = {"raw": "2"}  
        pagination.PageNumberPagination.page_size = request.GET.get('count_per_page', 10)
        if not request.GET.get("paginate"):
            self.pagination_class = None            
        
        response = super().list(request, *args, **kwargs)
        return Response(status=response.status_code, data={'status': 'SUCCESS', 'data': response.data })
    
    
    def create(self, request, *args, **kwargs):
        request.data._mutable = True
        request.data['created_by'] = request.user.id
        response = super().create(request, *args, **kwargs)        
        return Response(status=200, data={'status': 'SUCCESS', 'data': response.data})
        
        
    def partial_update(self, request, *args, **kwargs):
        request.data._mutable = True
        request.data['updated_by'] = request.user.id
        response = super().partial_update(request, *args, **kwargs)        
        return Response(status=200, data={'status': 'SUCCESS', 'data': response.data})
        
    
    def retrieve(self, request, *args, **kwargs):
        # values('branchs__medicine__medicine_category__name','branchs__medicine__name','name', 'branchs__medicine_id').
        self.serializer_class.context = {"raw": request.GET.get('raw')}
            
        medicine_list = Medicine.objects.prefetch_related('medicine_quantity').prefetch_related("branch").values(
            'medicine_quantity__qty', 'medicine_quantity__branch__name','medicine_quantity__medicine__name'
        ).filter(id=kwargs.get('pk')).exclude(medicine_quantity__branch__name=None)
        
        response = super().retrieve(request, *args, **kwargs)
        data = {
            'branch_list': medicine_list,
            'medicine': response.data
        }
        
        
        return Response(status=response.status_code, data={'status': 'SUCCESS', 'data': data })
     
    
    @action(detail=False,methods=['GET'])
    def category_list(self, request, *args, **kwargs):
        self.serializer_class = MedicineCategorySerializer
        category_list = MedicineCategory.objects.all().order_by('-created_at')
        category_serializer = self.get_serializer(category_list, many=True)
        return Response(status=status.HTTP_200_OK, data={'status': 'SUCCESS', 'data': category_serializer.data }) 
    
    @action(detail=False,methods=['POST'])
    def category_add(self, request, *args, **kwargs):
        serializer_obj = MedicineCategorySerializer(data=request.data)
        if serializer_obj.is_valid():
            serializer_obj.save()
        return Response(status=status.HTTP_200_OK, data={'status': 'SUCCESS', 'data': serializer_obj.data })
    
    # @action(detail=False,methods=['PATCH'])
    # def category_add(self, request, *args, **kwargs):
    #     serializer_obj = MedicineCategorySerializer(data=request.data)
    #     if serializer_obj.is_valid():
    #         serializer_obj.save()
    #     return Response(status=status.HTTP_200_OK, data={'status': 'SUCCESS', 'data': serializer_obj.data })
    
    
    
class PurchaseViewset(viewsets.ModelViewSet):
    queryset = Purchase.objects.select_related("vendor").order_by("-created_at")
    serializer_class = PurchaseSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['vendor__name', 'invoice_no']
    
    def list(self, request, *args, **kwargs):  
        pagination.PageNumberPagination.page_size = request.GET.get('count_per_page', 10)  
        if not request.GET.get("paginate"):
            self.pagination_class = None            
            
        self.serializer_class = PurchaseDetailSerializer   
        response = super().list(request, *args, **kwargs)
        return Response(status=response.status_code, data={'status': 'SUCCESS', 'data': response.data })
    
    
    def create(self, request, *args, **kwargs):
        request.data._mutable = True
        request.data['created_by'] = request.user.id
        response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            purchase_items = request.data.get('purchase_item')
            purchase_items = json.loads(purchase_items)
            
            items = []
            for item in purchase_items:
                items.append({
                    'medicine': item.get('medicine'),
                    'qty': item.get('qty'),
                    'price': item.get('price'),
                    'description': item.get('description'),
                    'purchase': response.data['id'],
                    'created_by': item.get('created_by')
                })
            
            purchase_obj = PurchaseItemSerializer(data=items, many=True)
            if purchase_obj.is_valid():
                purchase_obj.save()
            else:
                print("purchase_obj errors = ", purchase_obj.errors)
            
        return Response(status=200, data={'status': 'SUCCESS', 'data': response.data })
        
    
    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = PurchaseWithItemSerializer
        response = super().retrieve(request, *args, **kwargs)
        return Response(status=response.status_code, data={'status': 'SUCCESS', 'data': response.data })
    
    
    
class SalesViewset(viewsets.ModelViewSet):
    queryset = Sales.objects.order_by("-created_at")
    serializer_class = SalesSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['patient__name', 'invoice_no']
    
    def list(self, request, *args, **kwargs):  
        pagination.PageNumberPagination.page_size = request.GET.get('count_per_page', 10)  
        if not request.GET.get("paginate"):
            self.pagination_class = None            
            
        # self.serializer_class = Sale   
        response = super().list(request, *args, **kwargs)
        return Response(status=response.status_code, data={'status': 'SUCCESS', 'data': response.data })
    
    
    def create(self, request, *args, **kwargs):
        request.data._mutable = True
        request.data['created_by'] = request.user.id
        response = super().create(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_201_CREATED:
            medicine_list = request.data.getlist("medicine")
            qty_list = request.data.getlist("qty")
            price_list = request.data.getlist("price")
            items = []
            for index, medicine in enumerate(medicine_list):
                if qty_list[index]:
                    item = {
                        'sales': response.data['id'],
                        'medicine': medicine_list[index],
                        'qty': float(qty_list[index]),
                        'price': float(price_list[index])
                    }
                    items.append(item)
                 
            sales_obj = SalesItemSerializer(data=items, many=True)
            if sales_obj.is_valid():
                sales_obj.save()
            else:
                print("sales_obj errors = ", sales_obj.errors)
        
        data = {'sales': response.data,'sales_item': sales_obj.data}
        return Response(status=200, data={'status': 'SUCCESS', 'data': data })
        
 
 
class MedicineCategroyViewset(viewsets.ModelViewSet):
    queryset = MedicineCategory.objects.all().order_by("-created_at")
    serializer_class = MedicineCategorySerializer
    
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    
    def list(self, request, *args, **kwargs):    
        pagination.PageNumberPagination.page_size = request.GET.get('count_per_page', 10)
        if not request.GET.get("paginate"):
            self.pagination_class = None            
            
        # self.serializer_class = Sale   
        response = super().list(request, *args, **kwargs)
        return Response(status=response.status_code, data={'status': 'SUCCESS', 'data': response.data })
    
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return Response(status=response.status_code, data={'status': 'SUCCESS', 'data': response.data })
    
