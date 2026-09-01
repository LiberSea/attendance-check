from django.contrib import admin

from .models import AttendanceRecord, AttendanceSession


class AttendanceRecordInline(admin.TabularInline):
    model = AttendanceRecord
    extra = 0
    autocomplete_fields = ("student",)


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ("course", "date", "code", "is_open", "opened_at", "closed_at")
    list_filter = ("course", "date")
    search_fields = ("course__code", "course__name", "code")
    inlines = [AttendanceRecordInline]

    @admin.display(boolean=True, description="진행중")
    def is_open(self, obj):
        return obj.is_open


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ("session", "student", "status", "checked_at")
    list_filter = ("status", "session__course")
    search_fields = ("student__username", "student__student_id", "session__course__code")
    autocomplete_fields = ("session", "student")
