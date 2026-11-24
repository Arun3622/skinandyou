from django.contrib import admin

from api.appointment.models import Appointment, GoogleCalendarAppointment, Prescription, PrescriptionItem, AppointmentTreatment, AppointmentPatientImages


admin.site.register(Appointment)
admin.site.register(Prescription)
admin.site.register(PrescriptionItem)

admin.site.register(AppointmentTreatment)
admin.site.register(AppointmentPatientImages)

admin.site.register(GoogleCalendarAppointment)