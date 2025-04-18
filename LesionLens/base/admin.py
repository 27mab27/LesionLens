from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Patient, Diagnosis

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Extra Info", {
            "fields": ("role", "phone", "is_approved", "profile_photo")
        }),
    )
    list_display = ("username", "email", "role", "is_approved", "is_staff")
    list_filter = ("role", "is_approved")
    search_fields = ("username", "email", "phone")

admin.site.register(Patient)
admin.site.register(Diagnosis)
