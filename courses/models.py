from django.conf import settings
from django.db import models


class Course(models.Model):
    class Day(models.TextChoices):
        MON = "mon", "월"
        TUE = "tue", "화"
        WED = "wed", "수"
        THU = "thu", "목"
        FRI = "fri", "금"

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    professor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses_taught",
        limit_choices_to={"role": "professor"},
    )
    day_of_week = models.CharField(max_length=3, choices=Day.choices, null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    classroom = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.code} {self.name}"

    @property
    def has_schedule(self):
        return self.day_of_week and self.start_time and self.end_time

    def overlaps(self, other):
        if not self.has_schedule or not other.has_schedule:
            return False
        return self.day_of_week == other.day_of_week and self.start_time < other.end_time and other.start_time < self.end_time


class Enrollment(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
        limit_choices_to={"role": "student"},
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")

    class Meta:
        unique_together = ("student", "course")

    def __str__(self):
        return f"{self.student} - {self.course}"
