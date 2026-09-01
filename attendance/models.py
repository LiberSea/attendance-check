import random
import string

from django.conf import settings
from django.db import models

from courses.models import Course


def generate_code():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


class AttendanceSession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sessions")
    date = models.DateField()
    code = models.CharField(max_length=6, unique=True, default=generate_code)
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-opened_at"]

    def __str__(self):
        return f"{self.course} - {self.date}"

    @property
    def is_open(self):
        return self.closed_at is None


class AttendanceRecord(models.Model):
    class Status(models.TextChoices):
        PRESENT = "present", "출석"
        LATE = "late", "지각"
        ABSENT = "absent", "결석"

    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name="records")
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="attendance_records",
        limit_choices_to={"role": "student"},
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ABSENT)
    checked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("session", "student")

    def __str__(self):
        return f"{self.student} - {self.session} - {self.status}"
