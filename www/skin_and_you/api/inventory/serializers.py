from rest_framework import serializers

from api.inventory.models import Medicine, MedicineCategory, Purchase, PurchaseItem, Sales, SalesItem

        
class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine  
        fields = '__all__'
        
    def to_representation(self, instance):
        self.fields['created_at'] = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S')
        if self.context.get('raw') != "1":
            self.fields['medicine_category'] = serializers.SlugRelatedField(read_only=True, slug_field='name')
        return super().to_representation(instance)
    
class MedicineCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicineCategory
        fields = '__all__'
        
    def to_representation(self, instance):
        self.fields['created_at'] = serializers.DateTimeField(format='%d/%m/%Y %H:%m')
        return super().to_representation(instance)
    
    
    
class BranchDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine  
        fields = '__all__'
        
    def to_representation(self, instance):
        self.fields['created_at'] = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S')
        self.fields['medicine_category'] = MedicineCategorySerializer()
        return super().to_representation(instance)    
        
        

class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase  
        fields = '__all__'
        
    def to_representation(self, instance):
        self.fields['created_at'] = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S')
        self.fields['vendor'] = serializers.SlugRelatedField(slug_field='name', read_only=True)
        return super().to_representation(instance)    
        

class PurchaseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseItem
        fields = '__all__'
        
    def to_representation(self, instance):
        self.fields['created_at'] = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S')
        self.fields['medicine'] = serializers.SlugRelatedField(slug_field='name', read_only=True)
        return super().to_representation(instance)    
    

class PurchaseWithItemSerializer(serializers.ModelSerializer):
    purchase_item = serializers.SerializerMethodField()
    
    class Meta:
        model = Purchase
        fields = '__all__'
        
    def get_purchase_item(self, instance):
        items = PurchaseItem.objects.filter(purchase_id=instance.id)
        if items:
            return PurchaseItemSerializer(items, many=True).data
        return []
        
        
    def to_representation(self, instance):
        self.fields['vendor'] = serializers.SlugRelatedField(slug_field='name', read_only=True)
        self.fields['created_at'] = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S')
        return super().to_representation(instance)    

    

class PurchaseDetailSerializer(serializers.ModelSerializer):
    
    qty = serializers.SerializerMethodField()
    
    class Meta:
        model = Purchase  
        fields = '__all__'
        
    def get_qty(self, instance):
        return 0
        
    def to_representation(self, instance):
        self.fields['created_at'] = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S')
        self.fields['vendor'] = serializers.SlugRelatedField(slug_field='name', read_only=True)
        return super().to_representation(instance)    
    
    
    
class SalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sales  
        fields = '__all__'
        
            
    # def to_representation(self, instance):
    #     self.fields['created_at'] = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S')
    #     # self.fields['patient'] = serializers.SlugRelatedField(slug_field='name', read_only=True)
    #     return super().to_representation(instance)    
        

class SalesItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesItem
        fields = '__all__'
        
    def to_representation(self, instance):
        self.fields['created_at'] = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S')
        self.fields['medicine'] = serializers.SlugRelatedField(slug_field='name', read_only=True)
        self.fields['created_at'] = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S')
        return super().to_representation(instance)
    