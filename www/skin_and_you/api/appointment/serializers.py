from api.account.models import User, UserAddress
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from api.account.serializers import UserDetailSerializer, UserSerializer
from api.appointment.models import Appointment, AppointmentPatientAfterTreatmentImages, AppointmentPatientDisease, AppointmentPatientImages, AppointmentTreatment, Prescription, PrescriptionItem, PrescriptionTestsAdvised

from api.core.models import BranchUser, Patient, PatientFamily
from api.core.serializers import BranchSerializer, MedicineSerializer, PatientDataSerializer, PatientDetailSerializer, PatientFamilySerializer, PatientSerializer, SubDiseaseSerializer, UserAddressSerializer


class CalendarAppointmentSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Appointment
        fields = '__all__'
            
    def to_representation(self, instance):
        self.fields['patient'] = serializers.SlugRelatedField(read_only=True, slug_field='name')
        self.fields['doctor'] = serializers.SlugRelatedField(read_only=True, slug_field='name')
        self.fields['branch'] = serializers.SlugRelatedField(read_only=True, slug_field='name')
        self.fields['created_at'] = serializers.DateTimeField(format='%d/%m/%Y %H:%M')
        # self.fields['appointment_at'] = serializers.DateTimeField(format='%d/%m/%Y %H:%M')
        return super().to_representation(instance)
    
    
    
class PatientAppointmentSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Appointment
        fields = '__all__'
        
        
class AppointmentSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Appointment
        fields = '__all__'
            
    def to_representation(self, instance):
        self.fields['patient'] = serializers.SlugRelatedField(read_only=True, slug_field='name')
        self.fields['doctor'] = serializers.SlugRelatedField(read_only=True, slug_field='name')
        self.fields['branch'] = serializers.SlugRelatedField(read_only=True, slug_field='name')
        self.fields['created_at'] = serializers.DateTimeField(format='%d/%m/%Y %H:%M')
        self.fields['appointment_end_at'] = serializers.DateTimeField(format='%d/%m/%Y %H:%M')
        return super().to_representation(instance)
    
    

    
class AppointmentDetailsSerializer(serializers.ModelSerializer):    
    
    address = serializers.SerializerMethodField()
    family_detail = serializers.SerializerMethodField()
    patient_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = '__all__'
            
    def get_address(self, instance):
        user_address_list = UserAddress.objects.filter(user_id=instance.patient.id).order_by("created_at")
        print("user_address_list ", user_address_list)
        if user_address_list:
           data =  UserAddressSerializer(user_address_list[:1], many=True).data
           return data
        return []
    
    def get_family_detail(self, instance):
        family_list = PatientFamily.objects.filter(patient_id=instance.patient.id)
        print("family_list ", family_list)
        if family_list:
            return PatientFamilySerializer(family_list, many=True).data
        return []
    
    def get_patient_detail(self, instance):
        patient_list = Patient.objects.filter(user_id=instance.patient.id)
        print("patient_list ", patient_list)
        if patient_list:
            patient_obj = patient_list[0]
            return PatientDataSerializer(patient_obj).data
        
        
        return {}
            
    def to_representation(self, instance):
        self.fields['patient'] = UserSerializer()
        self.fields['doctor'] = UserSerializer()
        self.fields['branch'] = BranchSerializer()
        self.fields['created_at'] = serializers.DateTimeField(format='%d/%m/%Y %H:%M')
        self.fields['appointment_at'] = serializers.DateTimeField(format='%d/%m/%Y %H:%M')
        self.fields['appointment_end_at'] = serializers.DateTimeField(format='%d/%m/%Y %H:%M')
        return super().to_representation(instance)
    
    

class PrescriptionSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Prescription
        fields = '__all__'
            
    def to_representation(self, instance):
        self.fields['appointment'] = PatientAppointmentSerializer()
        self.fields['patient'] = serializers.SlugRelatedField(read_only=True, slug_field='name')
        self.fields['doctor'] = serializers.SlugRelatedField(read_only=True, slug_field='name')
        self.fields['branch'] = serializers.SlugRelatedField(read_only=True, slug_field='name')
        self.fields['created_at'] = serializers.DateTimeField(format='%d/%m/%Y %H:%M')
        return super().to_representation(instance)
    
    
class PrescriptionItemSerializer(serializers.ModelSerializer):
    medicine_id = serializers.SerializerMethodField()
        
    class Meta:
        model = PrescriptionItem
        fields = '__all__'
            
    def get_medicine_id(self, obj):
        return obj.medicine.id
    
    def to_representation(self, instance):
        # self.fields['prescription'] = PatientPrescriptionSerializer()
        self.fields['medicine'] = serializers.SlugRelatedField(read_only=True, slug_field='name')
        self.fields['created_at'] = serializers.DateTimeField(format='%d/%m/%Y %H:%M')
        return super().to_representation(instance)
    
    
    
class AppointmentTreatmentSerializer(serializers.ModelSerializer):    
    class Meta:
        model = AppointmentTreatment
        fields = '__all__'
            
    def to_representation(self, instance):
        self.fields['appointment'] = AppointmentSerializer()
        self.fields['patient'] = serializers.SlugRelatedField(read_only=True, slug_field='name')
        self.fields['doctor'] = serializers.SlugRelatedField(read_only=True, slug_field='name')
        self.fields['branch'] = serializers.SlugRelatedField(read_only=True, slug_field='name')
        self.fields['created_at'] = serializers.DateTimeField(format='%d/%m/%Y %H:%M')
        return super().to_representation(instance)
    
    
class AppointmentPatientImageSerializer(serializers.ModelSerializer):    
    class Meta:
        model = AppointmentPatientImages
        fields = '__all__'
    
    
class AppointmentPatientAfterImageSerializer(serializers.ModelSerializer):    
    class Meta:
        model = AppointmentPatientAfterTreatmentImages
        fields = '__all__'
    
    
class AppointmentPatientDiseaseSerializer(serializers.ModelSerializer):    
    class Meta:
        model = AppointmentPatientDisease
        fields = '__all__'
    
    
    
class AppointmentTreatmentDetailSerializer(serializers.ModelSerializer):    
    images = serializers.SerializerMethodField()
    after_images = serializers.SerializerMethodField()
    
    class Meta:
        model = AppointmentTreatment
        fields = '__all__'
        
    def get_images(self, instance):
        image_list = AppointmentPatientImages.objects.filter(appointment_treatment_id=instance.id)
        return AppointmentPatientImageSerializer(image_list, many=True).data
    
    def get_after_images(self, instance):
        image_list = AppointmentPatientAfterTreatmentImages.objects.filter(appointment_treatment_id=instance.id)
        return AppointmentPatientAfterImageSerializer(image_list, many=True).data
            
    def to_representation(self, instance):
        self.fields['appointment'] = AppointmentSerializer()
        self.fields['patient'] = serializers.SlugRelatedField(read_only=True, slug_field='name')
        self.fields['doctor'] = serializers.SlugRelatedField(read_only=True, slug_field='name')
        self.fields['branch'] = serializers.SlugRelatedField(read_only=True, slug_field='name')
        self.fields['sub_disease'] = SubDiseaseSerializer(many=True)
        self.fields['created_at'] = serializers.DateTimeField(format='%d/%m/%Y %H:%M')
        return super().to_representation(instance)
    
    
    
class AppointmentPrescriptionSerializer(serializers.ModelSerializer):    
    prescription = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = '__all__'
    
    def get_prescription(self, instance):
        prescription_list = PrescriptionItem.objects.filter(prescription__appointment_id=instance.id)
        if prescription_list:
            items = PrescriptionItemSerializer(prescription_list, many=True).data
            return items
        return []
            
        
            
    def to_representation(self, instance):
        self.fields['patient'] = serializers.SlugRelatedField(read_only=True, slug_field='name')
        self.fields['doctor'] = serializers.SlugRelatedField(read_only=True, slug_field='name')
        self.fields['branch'] = serializers.SlugRelatedField(read_only=True, slug_field='name')
        self.fields['created_at'] = serializers.DateTimeField(format='%d/%m/%Y %H:%M')
        self.fields['appointment_at'] = serializers.DateTimeField(format='%d/%m/%Y %H:%M')
        self.fields['appointment_end_at'] = serializers.DateTimeField(format='%d/%m/%Y %H:%M')
        return super().to_representation(instance)
    
    
    
    
class PrescriptionItemWithStockSerializer(serializers.ModelSerializer):    
    medicine_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = PrescriptionItem
        fields = '__all__'
        
    def get_medicine_stock(self, instance):
        return []
            
    def to_representation(self, instance):
        self.fields['prescription'] = PrescriptionSerializer()
        self.fields['medicine'] = MedicineSerializer()
        self.fields['created_at'] = serializers.DateTimeField(format='%d/%m/%Y %H:%M')
        return super().to_representation(instance)
    
    
    
class AppointmentTreatmentImageSerializer(serializers.ModelSerializer):    
    class Meta:
        model = AppointmentPatientImages
        fields = '__all__'
    
    
class TreatmentSerializer(serializers.ModelSerializer):    
    class Meta:
        model = AppointmentTreatment
        fields = '__all__'
        
        
        
class AdviceTestItemSerializer(serializers.ModelSerializer):
    advice_test_id = serializers.SerializerMethodField()
        
    class Meta:
        model = PrescriptionTestsAdvised
        fields = '__all__'
            
    def get_advice_test_id(self, obj):
        return obj.adviced_test.id
    
    def to_representation(self, instance):
        self.fields['adviced_test'] = serializers.SlugRelatedField(read_only=True, slug_field='name')
        self.fields['created_at'] = serializers.DateTimeField(format='%d/%m/%Y %H:%M')
        return super().to_representation(instance)