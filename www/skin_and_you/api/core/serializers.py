from api.account.models import User, UserAddress
from api.account.serializers import UserDetailSerializer, UserSerializer
from api.core.models import Branch, BranchUser, Disease, Patient, PatientFamily, StateMaster, CityMaster, SubDisease, TreatmentTestsMaster,UserRole, Vendor
from rest_framework import serializers

from api.inventory.models import Medicine



class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StateMaster  
        fields = '__all__'
        
        
class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CityMaster
        fields = '__all__'  
    
    
class UserAddressSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = UserAddress
        fields = '__all__'
        
    def to_representation(self, instance):
        self.fields['city'] = serializers.SlugRelatedField(read_only=True, slug_field='name')
        self.fields['state'] = serializers.SlugRelatedField(read_only=True, slug_field='name')
        return super().to_representation(instance)    
    

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch  
        fields = '__all__'
        
        
class BranchDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch  
        fields = '__all__'
        
    def to_representation(self, instance):
        self.fields['city'] = serializers.SlugRelatedField(read_only=True, slug_field='name')
        self.fields['state'] = serializers.SlugRelatedField(read_only=True, slug_field='name')
        self.fields['created_at'] = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S')
        return super().to_representation(instance)    
        
        
class BranchUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BranchUser  
        fields = '__all__'
                
        
        
class DiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disease  
        fields = '__all__'
        
    def to_representation(self, instance):
        self.fields['created_at'] = serializers.DateTimeField(format='%d/%m/%Y %H:%m')
        return super().to_representation(instance)   
        
        
class SubDiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubDisease  
        fields = '__all__'
    
    def to_representation(self, instance):
        self.fields['created_at'] = serializers.DateTimeField(format='%d/%m/%Y %H:%m')
        return super().to_representation(instance)   
        
        
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole  
        fields = '__all__'
        
        
class PatientFamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientFamily  
        fields = '__all__'
        
        
class PatientAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = '__all__'
    
   
class PatientDetailSerializer(serializers.ModelSerializer):
    
    address = serializers.SerializerMethodField()
    family_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = Patient  
        fields = '__all__'
        
    def get_address(self, instance):
        print("Self.context", self.context)
        
        user_address_list = UserAddress.objects.filter(user_id=instance.user_id)
        if user_address_list:
            if self.context.get('isUserAddressSerializer') == 1:
                print("In User Address Serializer")
                data =  UserAddressSerializer(user_address_list, many=True).data                 
            else:                
                print("In Patient Address Serializer")
                data =  PatientAddressSerializer(user_address_list, many=True).data                 
            return data
        return []
    
    def get_family_detail(self, instance):
        family_list = PatientFamily.objects.filter(patient_id=instance.user_id)
        if family_list:
            return PatientFamilySerializer(family_list, many=True).data
        return []
            
        
    def to_representation(self, instance):
        self.fields['user'] = UserDetailSerializer()
        self.fields['branch'] = BranchSerializer()
        self.fields['created_at'] = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S')
        self.fields['created_by'] = UserDetailSerializer()
        
        return super().to_representation(instance)
    
    
    
class PatientSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Patient  
        fields = '__all__'
            
    def to_representation(self, instance):
        self.fields['user'] = UserDetailSerializer()
        self.fields['branch'] = BranchSerializer()
        self.fields['created_at'] = serializers.DateTimeField(format='%d/%m/%Y')
        self.fields['created_by'] = UserDetailSerializer()
        return super().to_representation(instance)
    
    
    
class PatientDataSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Patient  
        fields = '__all__'
    
    
class UserProfileSerializer(serializers.ModelSerializer):
    
    address = serializers.SerializerMethodField()
    branch = serializers.SerializerMethodField()
    patient_treated = serializers.SerializerMethodField()
        
    class Meta:
        model = User  
        fields = '__all__'
        
    def get_branch(self, instance):
        if instance:
            branch_list = BranchUser.objects.filter(user_id=instance.id)
            if branch_list:
                branch_user_obj = branch_list[0]
                return BranchSerializer(branch_user_obj.branch).data
        return []
        
    def get_address(self, instance):
        user_address_list = UserAddress.objects.filter(user_id=instance.id).order_by("-created_at")
        if user_address_list:
            if self.context.get('isUserAddressSerializer') == 1:
                data =  UserAddressSerializer(user_address_list, many=True).data                 
            else:                
                data =  PatientAddressSerializer(user_address_list, many=True).data
            
            return data
        return []
    
    
    
    
    
    def get_patient_treated(self, instance):
        return 0
            
        
    def to_representation(self, instance):
        self.fields['created_at'] = serializers.DateTimeField(format='%d/%m/%Y')
        self.fields['created_by'] = UserDetailSerializer()
        self.fields['role'] = RoleSerializer()
        return super().to_representation(instance)
    
    
    
class MedicineSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Medicine  
        fields = '__all__'
        
        
class VendorSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Vendor  
        fields = '__all__'
        
    def to_representation(self, instance):
        self.fields['created_at'] = serializers.DateTimeField(format='%d/%m/%Y %H:%m')
        return super().to_representation(instance)
        
        
class UserRawDataSerializer(serializers.ModelSerializer):
    
    address = serializers.SerializerMethodField()
    branch = serializers.SerializerMethodField()
    # patient_treated = serializers.SerializerMethodField()
        
    class Meta:
        model = User  
        fields = '__all__'
        
    def get_branch(self, instance):
        if instance:
            branch_list = BranchUser.objects.filter(user_id=instance.id)
            if branch_list:
                branch_user_obj = branch_list[0]
                return BranchSerializer(branch_user_obj.branch).data
        return []
        
    def get_address(self, instance):
        user_address_list = UserAddress.objects.filter(user_id=instance.id).order_by("-created_at")
        if user_address_list:
            data =  PatientAddressSerializer(user_address_list, many=True).data
            return data
        return []
    
    
    
class TreatmentTestAdviceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TreatmentTestsMaster  
        fields = '__all__'