from django.core import mail
from django.test import TestCase
from django.urls import reverse

from .models import User


class SignUpTests(TestCase):
    def test_student_signup_requires_student_id(self):
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "username": "student1",
                "email": "student1@test.com",
                "role": "student",
                "student_id": "",
                "password1": "TestPass123!",
                "password2": "TestPass123!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="student1").exists())

    def test_professor_signup_succeeds_without_student_id(self):
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "username": "prof1",
                "email": "prof1@test.com",
                "role": "professor",
                "student_id": "",
                "password1": "TestPass123!",
                "password2": "TestPass123!",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="prof1", role=User.Role.PROFESSOR).exists())


class PasswordResetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="student1",
            email="student1@test.com",
            password="OldPass123!",
            role=User.Role.STUDENT,
            student_id="20240001",
        )

    def test_password_reset_sends_email(self):
        response = self.client.post(reverse("password_reset"), {"email": "student1@test.com"})
        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("student1", mail.outbox[0].body)
