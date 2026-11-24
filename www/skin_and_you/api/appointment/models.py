from django.db import models
from api.core.models import AuditMixin, TreatmentTestsMaster
import uuid


class Appointment(AuditMixin):
    STATUS_LIST = [
        ('Visited', 'Visited'),
        ('Not Visited', 'Not Visited'),
        ('Cancelled', 'Cancelled'),
        ('Pending', 'Pending')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doctor = models.ForeignKey("account.User", on_delete=models.PROTECT, related_name="appointment_doctor")
    patient = models.ForeignKey("account.User", on_delete=models.PROTECT, related_name="appointment_patient")
    branch = models.ForeignKey("core.Branch", on_delete=models.PROTECT, related_name="appointment_branch")
    about_disease = models.CharField(max_length=500, null=True, blank=True)
    appointment_at = models.DateTimeField(db_index=True)
    appointment_end_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(choices=STATUS_LIST, default="Pending", max_length=11)
    visited_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = "appointment"
        # unique_together = ('appointment_at', 'status', 'patient')
        
        

class Prescription(AuditMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doctor = models.ForeignKey("account.User", on_delete=models.PROTECT, related_name="prescription_doctor")
    patient = models.ForeignKey("account.User", on_delete=models.PROTECT, related_name="prescription_patient")
    branch = models.ForeignKey("core.Branch", on_delete=models.PROTECT, related_name="prescription_branch")
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name="prescription_appointment")
     
    class Meta:
        db_table = "patient_prescription"
        unique_together = ('doctor', 'patient', 'branch', 'appointment')
        
    def __str__(self) -> str:
        return str(self.appointment.id)
        
        
class PrescriptionItem(AuditMixin):
    FREQUENCY_LIST  = [
        ('Once Daily',  'Once Daily'),
        ('Twice Daily',  'Twice Daily'),
        ('Three Times Daily',  'Three Times Daily'),
        ('Four Times Daily',  'Four Times Daily'),
        ('Every 30 Minutes',  'Every 30 Minutes'),
        ('Every Hour',  'Every Hour'),
        ('Every Eight Hours',  'Every Eight Hours'),
        ('Every Ten Hours',  'Every Ten Hours'),
        ('Every Twelve Hours',  'Every Twelve Hours'),
        ('Every Alternate Days',  '"Every Alternate Days'),
        ('Every Two Days',  'Every Two Days'),
        ('Every Three Days',  'Every Three Days'),
        ('Every Four Days',  'Every Four Days'),
        ('Every Five Days',  'Every Five Days'),
        ('Every Six Days',  'Every Six Days'),
        ('Every Seven Days',  'Every Seven Days'),
        ('Every Week',  'Every Week'),
    ] 
        
    DURATION_LIST  = [
        ('Day(s)',  'Day(s)'),
        ('Week(s)',  'Week(s)'),
        ('Month(s)',  'Month(s)'),
        ('Year(s)',  'Year(s)'),
    ] 
    
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name="prescription_item")
    medicine = models.ForeignKey("inventory.Medicine",  on_delete=models.PROTECT, related_name="prescription_medicine")
    
    dose = models.CharField(max_length=10)
    frequency = models.CharField(max_length=35)
    duration_count = models.CharField(max_length=10)
    duration_name = models.CharField(max_length=25)
    
    instruction = models.CharField(max_length=500, null=True, blank=True)
    
    class Meta:
        db_table = "patient_prescription_item"
        unique_together = ('prescription', 'medicine')
        
    def __str__(self) -> str:
        return str(self.prescription.id)
    
    
    
class PrescriptionTestsAdvised(AuditMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name="prescription_test")
    adviced_test = models.ForeignKey(TreatmentTestsMaster, on_delete=models.CASCADE, related_name="prescription_adviced_test")
    fasting_pardial = models.CharField(max_length=50, null=True, blank=True)
    remark = models.CharField(max_length=1000, blank=True, null=True)
    
    class Meta:
        db_table = "patient_prescription_test_advice"
        # unique_together = ('prescription', 'adviced_test')
        
    def __str__(self) -> str:
        return str(self.prescription.id)


class AppointmentTreatment(AuditMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doctor = models.ForeignKey("account.User", on_delete=models.PROTECT, related_name="attended_doctor")
    patient = models.ForeignKey("account.User", on_delete=models.PROTECT, related_name="attended_patient")
    branch = models.ForeignKey("core.Branch", on_delete=models.PROTECT, related_name="attended_branch")
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name="attended_appointment")
    sub_disease = models.ManyToManyField("core.SubDisease", null=True, blank=True)
    observation = models.CharField(max_length=1000, null=True, blank=True)
    remark = models.CharField(max_length=1000, null=True, blank=True)
    technician_name = models.CharField(max_length=255, null=True, blank=True)
    medical_history = models.CharField(max_length=1000, null=True, blank=True)
    procedure_history = models.CharField(max_length=1000, null=True, blank=True)
     
    class Meta:
        db_table = "patient_treatment"
        unique_together = ('doctor', 'patient', 'branch', 'appointment')
        
        
class AppointmentPatientImages(AuditMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment_treatment = models.ForeignKey(AppointmentTreatment, on_delete=models.CASCADE, related_name="appointment_treatment_images")
    appointment = models.ForeignKey(Appointment, on_delete=models.PROTECT, related_name="appointment_patient_image")
    image = models.ImageField(upload_to="media/patient")
     
    class Meta:
        db_table = "patient_treatment_images"
        
        
class AppointmentPatientAfterTreatmentImages(AuditMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment_treatment = models.ForeignKey(AppointmentTreatment, on_delete=models.CASCADE, related_name="appointment_after_treatment_images")
    appointment = models.ForeignKey(Appointment, on_delete=models.PROTECT, related_name="appointment_patient_after_image")
    image = models.ImageField(upload_to="media/patient")
     
    class Meta:
        db_table = "patient_after_treatment_images"
        
        
class AppointmentPatientDisease(AuditMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment_treatment = models.ForeignKey(AppointmentTreatment, on_delete=models.CASCADE, related_name="appointment_after_treatment_disease")
    appointment = models.ForeignKey(Appointment, on_delete=models.PROTECT, related_name="appointment_patient_disease")
    sub_disease = models.ManyToManyField("core.SubDisease", null=True, blank=True)
     
    class Meta:
        db_table = "appointment_patient_disease"
        
        
        
class GoogleCalendarAppointment(AuditMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment = models.ForeignKey(Appointment, on_delete=models.PROTECT, related_name="google_appointment")
    google_calendar_event_id = models.TextField(max_length=500, null=True, blank=True)
    google_response = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = "google_calendar_log"
        
        
        