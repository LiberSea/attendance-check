from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from courses.models import Course

from .models import AttendanceRecord, AttendanceSession


class AttendanceFlowTests(TestCase):
    def setUp(self):
        self.professor = User.objects.create_user(
            username="prof1", password="TestPass123!", role=User.Role.PROFESSOR
        )
        self.student = User.objects.create_user(
            username="student1",
            password="TestPass123!",
            role=User.Role.STUDENT,
            student_id="20240001",
        )
        self.outsider = User.objects.create_user(
            username="student2",
            password="TestPass123!",
            role=User.Role.STUDENT,
            student_id="20240002",
        )
        self.course = Course.objects.create(name="자료구조", code="CS201", professor=self.professor)
        self.course.enrollments.create(student=self.student)

    def test_professor_can_open_session(self):
        self.client.force_login(self.professor)
        response = self.client.post(reverse("attendance:session_open", args=[self.course.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(AttendanceSession.objects.filter(course=self.course).count(), 1)

    def test_student_can_check_in_with_correct_code(self):
        session = AttendanceSession.objects.create(course=self.course, date="2026-09-01")
        self.client.force_login(self.student)
        response = self.client.post(reverse("attendance:check_in", args=[session.pk]), {"code": session.code})
        self.assertRedirects(response, reverse("attendance:session_detail", args=[session.pk]))
        record = AttendanceRecord.objects.get(session=session, student=self.student)
        self.assertEqual(record.status, AttendanceRecord.Status.PRESENT)
        self.assertIsNotNone(record.checked_at)

    def test_check_in_fails_with_wrong_code(self):
        session = AttendanceSession.objects.create(course=self.course, date="2026-09-01")
        self.client.force_login(self.student)
        response = self.client.post(reverse("attendance:check_in", args=[session.pk]), {"code": "WRONG1"})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(AttendanceRecord.objects.filter(session=session, student=self.student).exists())

    def test_outsider_cannot_check_in(self):
        session = AttendanceSession.objects.create(course=self.course, date="2026-09-01")
        self.client.force_login(self.outsider)
        response = self.client.post(reverse("attendance:check_in", args=[session.pk]), {"code": session.code})
        self.assertEqual(response.status_code, 403)

    def test_closing_session_marks_uncheckedin_students_absent(self):
        session = AttendanceSession.objects.create(course=self.course, date="2026-09-01")
        self.client.force_login(self.professor)
        response = self.client.post(reverse("attendance:session_close", args=[session.pk]))
        self.assertEqual(response.status_code, 302)
        session.refresh_from_db()
        self.assertFalse(session.is_open)
        record = AttendanceRecord.objects.get(session=session, student=self.student)
        self.assertEqual(record.status, AttendanceRecord.Status.ABSENT)

    def test_cannot_check_in_after_close(self):
        session = AttendanceSession.objects.create(course=self.course, date="2026-09-01")
        session.closed_at = "2026-09-01T00:00:00Z"
        session.save()
        self.client.force_login(self.student)
        response = self.client.post(reverse("attendance:check_in", args=[session.pk]), {"code": session.code})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(AttendanceRecord.objects.filter(session=session, student=self.student, status="present").exists())


class AttendanceStatsTests(TestCase):
    def setUp(self):
        self.professor = User.objects.create_user(
            username="prof1", password="TestPass123!", role=User.Role.PROFESSOR
        )
        self.student = User.objects.create_user(
            username="student1",
            password="TestPass123!",
            role=User.Role.STUDENT,
            student_id="20240001",
        )
        self.course = Course.objects.create(name="자료구조", code="CS201", professor=self.professor)
        self.course.enrollments.create(student=self.student)

    def test_stats_page_requires_owner(self):
        session = AttendanceSession.objects.create(course=self.course, date="2026-09-01")
        session.records.create(student=self.student, status=AttendanceRecord.Status.PRESENT)
        self.client.force_login(self.student)
        response = self.client.get(reverse("attendance:course_stats", args=[self.course.pk]))
        self.assertEqual(response.status_code, 403)

    def test_stats_page_shows_attendance_rate(self):
        session = AttendanceSession.objects.create(course=self.course, date="2026-09-01", closed_at=timezone.now())
        session.records.create(student=self.student, status=AttendanceRecord.Status.PRESENT)
        self.client.force_login(self.professor)
        response = self.client.get(reverse("attendance:course_stats", args=[self.course.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "100.0%")

    def test_csv_export(self):
        session = AttendanceSession.objects.create(course=self.course, date="2026-09-01")
        session.records.create(student=self.student, status=AttendanceRecord.Status.PRESENT)
        self.client.force_login(self.professor)
        response = self.client.get(reverse("attendance:export_csv", args=[self.course.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        content = response.content.decode("utf-8-sig")
        self.assertIn("20240001", content)
        self.assertIn("출석", content)


class QrCodeTests(TestCase):
    def setUp(self):
        self.professor = User.objects.create_user(
            username="prof1", password="TestPass123!", role=User.Role.PROFESSOR
        )
        self.student = User.objects.create_user(
            username="student1",
            password="TestPass123!",
            role=User.Role.STUDENT,
            student_id="20240001",
        )
        self.course = Course.objects.create(name="자료구조", code="CS201", professor=self.professor)
        self.course.enrollments.create(student=self.student)
        self.session = AttendanceSession.objects.create(course=self.course, date="2026-09-01")

    def test_professor_can_view_qr_image(self):
        self.client.force_login(self.professor)
        response = self.client.get(reverse("attendance:session_qr", args=[self.session.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/png")

    def test_student_cannot_view_qr_image(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("attendance:session_qr", args=[self.session.pk]))
        self.assertEqual(response.status_code, 403)

    def test_check_in_form_prefills_code_from_query_param(self):
        self.client.force_login(self.student)
        response = self.client.get(
            reverse("attendance:check_in", args=[self.session.pk]) + f"?code={self.session.code}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.session.code)
