from django.contrib import admin
from .models import *

# =========================================================
# OTHER MODELS
# =========================================================

admin.site.register(Doctor)
admin.site.register(Appointment)
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
admin.site.register(SubDepartment)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Wishlist)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Address)

# =========================================================
# PRODUCTS
# =========================================================

admin.site.register(Product)

# =========================================================
# CUSTOMERS
# =========================================================
@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'patient_name',
        'email',
        'phone',
        'registered_date',
    )

    search_fields = (
        'user__first_name',
        'user__last_name',
        'user__email',
        'user__username',
        'phone',
    )

    list_filter = (
        'created_at',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    ordering = (
        '-created_at',
    )

    def patient_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    patient_name.short_description = 'Patient Name'

    def email(self, obj):
        return obj.user.email

    email.short_description = 'Email'

    def registered_date(self, obj):
        return obj.created_at.strftime('%d %b %Y')

    registered_date.short_description = 'Registered'