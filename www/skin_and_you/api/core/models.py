import uuid
from django.db import models


class AuditMixin(models.Model):
    # It is common field to use in each model.
    created_by = models.ForeignKey('account.User', db_column="created_by", on_delete=models.CASCADE,
                                   related_name="created_by_%(app_label)s_%(class)s_set", null=True, blank=True)
    
    updated_by = models.ForeignKey('account.User', db_column="updated_by", on_delete=models.CASCADE, null=True,
                                   blank=True,
                                   related_name="modified_by_%(app_label)s_%(class)s_set")

    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    update_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
        
            
class StateMaster(AuditMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, unique=True)
    
    class Meta:
        db_table = "state_master"
        
    def __str__(self):
        return self.name
    
    
class CityMaster(AuditMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    state = models.ForeignKey(StateMaster, on_delete=models.PROTECT)
    name = models.CharField(max_length=150)
    
    class Meta:
        db_table = "city_master"
        unique_together = ("state", "name",)
        
    def __str__(self):
        return self.name

            
class Disease(AuditMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, unique=True)
    
    class Meta:
        db_table = "disease_master"
    
    
class SubDisease(AuditMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    disease_for = models.CharField(max_length=75, null=True, blank=True)
    name = models.CharField(max_length=150, unique=True)
    
    class Meta:
        db_table = "sub_disease_master"
    
        
# class Medicine(AuditMixin):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     sku_code = models.CharField(max_length=20, unique=True)
#     name = models.CharField(max_length=150, unique=True)
#     weight = models.CharField(max_length=300)
#     description = models.TextField(max_length=1000)
#     quantity = models.IntegerField(default=0)
#     price = models.DecimalField(max_digits=8, decimal_places=3, default=0)
    
#     class Meta:
#         db_table = "medicine_master"
#         unique_together = ("sku_code", "name",)    
        
        
class Branch(AuditMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=150)
    
    email = models.CharField(max_length=254, null=True, blank=True)
    telephone = models.CharField(max_length=15, null=True, blank=True)
    mobile = models.CharField(max_length=15, null=True, blank=True)
    
    address = models.CharField(max_length=300, null=True, blank=True)
    pincode = models.CharField(max_length=6, null=True, blank=True)
    state = models.ForeignKey(StateMaster, on_delete=models.PROTECT)
    city = models.ForeignKey(CityMaster, on_delete=models.PROTECT)
    country = models.CharField(max_length=75, default="India")
    
    class Meta:
        db_table = "branch"
        
    def __str__(self):
        return f" {self.name} - {self.code} "
    

class BranchUser(AuditMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("account.User", on_delete=models.PROTECT, related_name="branch_users")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="branch_user_mapper")
    is_branch_owner = models.BooleanField(default=False)
    
    class Meta:
        db_table = "branch_user"
        
    def __str__(self):
        return f" {self.branch.name} "


class BranchRoom(AuditMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room_no = models.PositiveIntegerField(default=0)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT)
    
    class Meta:
        db_table = "branch_room"
        unique_together = ("branch", "room_no")
        
        
# class MedicineForDisease(AuditMixin):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT)
#     disease = models.ForeignKey(Disease, on_delete=models.PROTECT)
#     sub_disease = models.ForeignKey(SubDisease, on_delete=models.PROTECT, null=True, blank=True)
    
#     class Meta:
#         db_table = "medicine_for_disease"
        
        
class UserRole(AuditMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=25, unique=True)
    
    class Meta:
        db_table = "user_role"
    
    def __str__(self):
        return self.name
    
    
 
class PatientBackground(AuditMixin):   
    age = models.PositiveIntegerField()
    allergy_or_oral_contraceptive = models.CharField(max_length=500, null=True, blank=True)
    menstrual_child_birth_history = models.CharField(max_length=500, null=True, blank=True)
    hair_complaints = models.CharField(max_length=500, null=True, blank=True)
    nail_compalints = models.CharField(max_length=500, null=True, blank=True)
    weight_gain_loss_in_3_months = models.CharField(max_length=500, null=True, blank=True)
    diet = models.CharField(max_length=500, null=True, blank=True)
    excercise = models.CharField(max_length=500, null=True, blank=True)
    sleeping_habits = models.CharField(max_length=500, null=True, blank=True)
    
    has_smoking = models.BooleanField(default=False)
    has_alcoholic = models.BooleanField(default=False)
    has_pets = models.BooleanField(default=False)
    has_sunscreen_use = models.BooleanField(default=False)
    has_outdoor_activities = models.BooleanField(default=False)
    has_skin_care_activity = models.BooleanField(default=False)    
    
    class Meta:
        abstract = True
    
    
class Patient(PatientBackground):
    user = models.OneToOneField("account.User", on_delete=models.CASCADE, primary_key=True, related_name="patent_user_mapper")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    medical_record_no = models.IntegerField(default=0)
    
    dermatology_concern = models.CharField(max_length=500, null=True, blank=True)
    other_dermatology_concern = models.CharField(max_length=500, null=True, blank=True)
    cosmetic_concern = models.CharField(max_length=500, null=True, blank=True) 
    other_cosmetic_concern = models.CharField(max_length=500, null=True, blank=True) 
    
    class Meta:
        db_table = "patient"
        
    def __str__(self):
        return f"{self.user.name} - {self.user.email}"
        

class PatientFamily(PatientBackground):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey("account.User", on_delete=models.PROTECT)
    relationship = models.CharField(max_length=15)
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
        
    interested_in_offer = models.BooleanField(default=False)
    
    class Meta:
        db_table = "patient_family"


class PatientDiesease(AuditMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey("account.User", on_delete=models.PROTECT)
    disease = models.ForeignKey("core.Disease", on_delete=models.PROTECT)
    sub_disease = models.ForeignKey("core.SubDisease", on_delete=models.PROTECT)
    dermatology_concern = models.CharField(max_length=300)
    other_dermatology_concern = models.CharField(max_length=300, null=True, blank=True)
    cosmetic_concern = models.CharField(max_length=300, null=True, blank=True) 
    other_cosmetic_concern = models.CharField(max_length=300, null=True, blank=True) 
    
    class Meta:
        db_table = "patient_diesease"


class PatientDoctor(AuditMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doctor = models.ForeignKey("account.User", on_delete=models.PROTECT, related_name="user_doctor")
    patient = models.ForeignKey("account.User", on_delete=models.PROTECT, related_name="user_patient")
    
    class Meta:
        db_table = "patient_doctor"
        
        
class Vendor(AuditMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=254)
    contact = models.CharField(max_length=15, null=True, blank=True)
    
    class Meta:
        db_table = "vendor"
        
    def __str__(self):
        return f" {self.name} "


class TreatmentTestsMaster(AuditMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = "treatment_tests_master"
        
    def __str__(self):
        return f" {self.name} "

    