from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "학생"
        PROFESSOR = "professor", "교수"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    student_id = models.CharField(max_length=20, unique=True, null=True, blank=True)

    def __str__(self):
        return self.username
