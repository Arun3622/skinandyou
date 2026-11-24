from django.apps import AppConfig


class AppointmentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api.appointment'
    
    def ready(self):
        import api.appointment.signals