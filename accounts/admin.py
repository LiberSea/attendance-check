from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "role", "student_id", "is_staff")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("username", "email", "student_id")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("역할 정보", {"fields": ("role", "student_id")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("역할 정보", {"fields": ("role", "student_id")}),
    )


admin.site.register(User, UserAdmin)
