from datetime import datetime
from django.db import models

from api.core.models import AuditMixin

import uuid


class MedicineCategory(AuditMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, unique=True)
    
    class Meta:
        db_table = "medicine_category"
        
    def __str__(self):
        return f"{self.name}"
                
        
class Medicine(AuditMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    medicine_category = models.ForeignKey(MedicineCategory, on_delete=models.PROTECT, related_name='medicines')
    sku_code = models.CharField(max_length=150, unique=True)
    name = models.CharField(max_length=150)
    content = models.CharField(max_length=500, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    total_qty = models.IntegerField(default=0)
    serial_number = models.IntegerField(default=0)
    opening_qty = models.IntegerField(null=True, blank=True)
       
    class Meta:
        db_table = "medicine"
        
    def __str__(self):
        return f"{self.sku_code} - {self.name}"
        

class MedicineQty(AuditMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT, related_name='medicine_quantity')
    branch = models.ForeignKey("core.Branch", on_delete=models.PROTECT, related_name='branchs')
    qty = models.IntegerField(default=0)
       
    class Meta:
        db_table = "medicine_qty"
        unique_together = ('medicine', 'branch')
        
    def __str__(self):
        return f"{self.medicine.sku_code} - {self.qty}"
        
        
class MedicineForDisease(AuditMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    medicine = models.ForeignKey(MedicineCategory, on_delete=models.PROTECT, related_name='medicine_disease')
    disease = models.ForeignKey("core.SubDisease", on_delete=models.PROTECT, related_name='diseases')
       
    class Meta:
        db_table = "medicine_for_disease"
        unique_together = ('medicine', 'disease')
        
    def __str__(self):
        return f"{self.medicine.sku_code} - {self.disease}"
    
    
        
class Purchase(AuditMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor = models.ForeignKey("core.Vendor", on_delete=models.PROTECT, related_name='vendor_purchase')
    invoice_no = models.CharField(max_length=15, unique=True)
    invoice_date = models.DateField()
    invoice = models.FileField(upload_to="purchase", null=True, blank=True)
    
    class Meta:
        db_table = "purchase"
        
    def __str__(self):
        return f"{self.invoice_no} - {self.vendor.name}"
    
    
class PurchaseItem(AuditMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase = models.ForeignKey(Purchase, on_delete=models.PROTECT, related_name='purchase_invoice')
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT, related_name='purchase_medince')
    qty = models.DecimalField(max_digits=12, decimal_places=6)
    price = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    
    class Meta:
        db_table = "purchase_item"
        
    def __str__(self):
        return f"{self.purchase.invoice_no} - {self.purchase.vendor.name}"
    
    
class Sales(AuditMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey("core.Patient", on_delete=models.PROTECT, related_name='sales_patient')
    prescription = models.ForeignKey("appointment.Prescription", on_delete=models.PROTECT, related_name='sales_prescription', null=True, blank=True)
    invoice_no = models.CharField(max_length=15, null=True,blank=True)
    invoice_date = models.DateField(null=True, blank=True)
    
    class Meta:
        db_table = "sales"
        
    def __str__(self):
        return f"{self.invoice_no}"
    
    def save(self, *args, **kwargs):
        if  kwargs.get('force_insert'):        
            try:
                sales_obj = Sales.objects.latest("created_at")
                invoice_no = sales_obj.invoice_no            
            except:
                invoice_no = 0
                
            self.invoice_no = int(invoice_no)+1
            self.invoice_date = datetime.today().date()
        super().save(*args, **kwargs)
    
    
class SalesItem(AuditMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sales = models.ForeignKey(Sales, on_delete=models.PROTECT, related_name='sales_invoice')
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT, related_name='sales_medicine')
    qty = models.DecimalField(max_digits=12, decimal_places=6)
    price = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True)
    
    class Meta:
        db_table = "sales_item"
        
    def __str__(self):
        return f"{self.medicine.name}"