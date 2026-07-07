from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Doctor)
admin.site.register(Appointment)
admin.site.register(Patient)
admin.site.register(Department)
admin.site.register(Summary)
admin.site.register(RazorpayPaymentDetails)
admin.site.register(Leave)
admin.site.register(MonthlyTiming)
admin.site.register(HealthCheckupBooking)
admin.site.register(HealthCheckupPlan)
admin.site.register(Notification)
admin.site.register(AvailableTime)
admin.site.register(Blog)
admin.site.register(BlogComment)
admin.site.register(Message)
