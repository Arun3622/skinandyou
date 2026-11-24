from datetime import timedelta
import json
from django.conf import settings
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from api.account.utils import create_google_calendar_event
from api.appointment.models import Appointment, GoogleCalendarAppointment, Prescription, AppointmentTreatment
from django.utils import timezone

from api.inventory.models import PurchaseItem, SalesItem
from django.db.models import Sum


def update_appointment_status(instance):
    appointment_instance = instance.appointment
    appointment_instance.status = "Visited"
    appointment_instance.visited_at = timezone.now()
    appointment_instance.save()
    return True

def manage_inventory(medicine_instance):
    print("Instance Manage Inventory Signal === ", medicine_instance)
        
    purchase_item = PurchaseItem.objects.filter(medicine=medicine_instance).aggregate(purchase_qty=Sum('qty'))
    sales_item = SalesItem.objects.filter(medicine=medicine_instance).aggregate(sales_qty=Sum('qty'))
    opening_qty = medicine_instance.opening_qty
    if not opening_qty:
        opening_qty = 0
    
    purchase_qty = purchase_item.get('purchase_qty', 0)
    sales_qty = sales_item.get('sales_qty', 0)
    
    if not purchase_qty:
        purchase_qty = 0
    
    if not sales_qty:
        sales_qty = 0
    
    total_qty = (purchase_qty+opening_qty) - sales_qty
        
    medicine_instance.total_qty = total_qty
    medicine_instance.save()
    
    # print(" ===  ", medicine_instance.id, " === ", total_qty)
    

@receiver(post_save, sender=Prescription)
def change_appointment_status_from_prescription(sender, instance, **kwargs):
    update_appointment_status(instance)
    return instance

@receiver(post_save, sender=AppointmentTreatment)
def change_appointment_status_from_treatment(sender, instance, **kwargs):
    update_appointment_status(instance)
    return instance


@receiver(post_save, sender=PurchaseItem)
def manage_from_purchase(sender, instance, **kwargs):
    print("Purchase Signal Called")
    purchase_items = PurchaseItem.objects.filter(purchase=instance.purchase)
    for item in purchase_items:
        manage_inventory(item.medicine)
    return instance


@receiver(post_save, sender=SalesItem)
def manage_from_sales(sender, instance, **kwargs):
    print("Sales Signal Called")
    sales_items = SalesItem.objects.filter(sales=instance.sales)
    for item in sales_items:
        manage_inventory(item.medicine)
        
    return instance





@receiver(post_save, sender=Appointment)
def add_to_google_calendar(sender, instance, **kwargs):
    if getattr(settings, "LOCAL_OFFLINE", False):
        return

    print("Appointment Signal Start Called")
    
    start_date = instance.appointment_at
    end_date = instance.appointment_end_at
    # end_date =  instance.appointment_at + timedelta(hours=1)
    
    try:
        start = start_date.strftime("%I:%M %p")
        end = end_date.strftime("%I:%M %p")
        
        data = {
            'summary': f"{instance.patient.name}",
            'location': f" {instance.about_disease}",
            'description': "Clinic appointment",
            'start_date': str(start_date).replace(" ", "T"),
            'end_date': str(end_date).replace(" ", "T"),
            'doctor_email': instance.doctor.email,
            'attendees': [
                {'email': instance.doctor.email},
                # Add as many as you need
            ]
        }
        event_info = create_google_calendar_event(data)
        # Save Google Log Calendar Event
        obj = GoogleCalendarAppointment(
            appointment_id=instance.id, 
            google_calendar_event_id=event_info['id'], 
            google_response=json.dumps(event_info)
        )
        obj.save()


        print("calendar event_info ", event_info)
    except Exception as e:
        print('Some went wrong with Google Calendar', str(e))
    
    print("Appointment Signal End")
    
    return instance


