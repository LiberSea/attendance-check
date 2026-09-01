import random
import string
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from courses.models import Course


def generate_code():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


class AttendanceSession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sessions")
    date = models.DateField()
    code = models.CharField(max_length=6, unique=True, default=generate_code)
    duration_minutes = models.PositiveIntegerField(default=15, help_text="세션이 자동으로 마감되기까지의 시간(분)")
    late_after_minutes = models.PositiveIntegerField(default=5, help_text="이 시간(분) 이후 체크인은 지각으로 처리")
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-opened_at"]

    def __str__(self):
        return f"{self.course} - {self.date}"

    @property
    def auto_close_at(self):
        return self.opened_at + timedelta(minutes=self.duration_minutes)

    @property
    def is_open(self):
        return self.closed_at is None and timezone.now() < self.auto_close_at

    @property
    def is_finalized(self):
        return self.closed_at is not None

    def status_for_checkin_time(self, checkin_time):
        late_at = self.opened_at + timedelta(minutes=self.late_after_minutes)
        return AttendanceRecord.Status.LATE if checkin_time > late_at else AttendanceRecord.Status.PRESENT


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
