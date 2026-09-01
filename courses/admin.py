from django.contrib import admin

from .models import Course, Enrollment


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 0
    autocomplete_fields = ("student",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "professor", "enrollment_count")
    list_filter = ("professor",)
    search_fields = ("code", "name", "professor__username")
    inlines = [EnrollmentInline]

    @admin.display(description="수강생 수")
    def enrollment_count(self, obj):
        return obj.enrollments.count()


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course")
    list_filter = ("course",)
    search_fields = ("student__username", "student__student_id", "course__code", "course__name")
    autocomplete_fields = ("student", "course")
