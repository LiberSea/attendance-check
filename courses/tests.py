from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from courses.models import Course


class CourseFlowTests(TestCase):
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

    def test_professor_can_create_course(self):
        self.client.force_login(self.professor)
        response = self.client.post(
            reverse("courses:create"), {"name": "자료구조", "code": "CS201"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Course.objects.filter(code="CS201", professor=self.professor).exists())

    def test_student_cannot_create_course(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse("courses:create"), {"name": "자료구조", "code": "CS202"}
        )
        self.assertEqual(response.status_code, 403)

    def test_student_can_enroll_with_code(self):
        course = Course.objects.create(name="자료구조", code="CS201", professor=self.professor)
        self.client.force_login(self.student)
        response = self.client.post(reverse("courses:enroll"), {"code": "CS201"})
        self.assertRedirects(response, reverse("courses:detail", args=[course.pk]))
        self.assertTrue(course.enrollments.filter(student=self.student).exists())

    def test_course_detail_shows_enrolled_students_to_professor(self):
        course = Course.objects.create(name="자료구조", code="CS201", professor=self.professor)
        course.enrollments.create(student=self.student)

        self.client.force_login(self.professor)
        response = self.client.get(reverse("courses:detail", args=[course.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "student1")
        self.assertContains(response, "20240001")

    def test_outsider_student_cannot_view_course_detail(self):
        course = Course.objects.create(name="자료구조", code="CS201", professor=self.professor)
        outsider = User.objects.create_user(
            username="student2", password="TestPass123!", role=User.Role.STUDENT, student_id="20240002"
        )
        self.client.force_login(outsider)
        response = self.client.get(reverse("courses:detail", args=[course.pk]))
        self.assertEqual(response.status_code, 403)


class TimetableTests(TestCase):
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
        self.course_a = Course.objects.create(
            name="자료구조", code="CS201", professor=self.professor,
            day_of_week=Course.Day.MON, start_time="09:00", end_time="10:00", classroom="공학관 401",
        )
        self.course_b = Course.objects.create(
            name="알고리즘", code="CS301", professor=self.professor,
            day_of_week=Course.Day.MON, start_time="09:30", end_time="11:00", classroom="공학관 402",
        )
        self.course_c = Course.objects.create(
            name="운영체제", code="CS302", professor=self.professor,
            day_of_week=Course.Day.TUE, start_time="09:00", end_time="10:00", classroom="공학관 403",
        )

    def test_timetable_shows_scheduled_courses(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("courses:timetable"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "자료구조")
        self.assertContains(response, "알고리즘")
        self.assertContains(response, "운영체제")

    def test_student_can_enroll_by_clicking(self):
        self.client.force_login(self.student)
        response = self.client.post(reverse("courses:enroll_click", args=[self.course_a.pk]))
        self.assertRedirects(response, reverse("courses:timetable"))
        self.assertTrue(self.course_a.enrollments.filter(student=self.student).exists())

    def test_time_conflict_blocks_second_enrollment(self):
        self.client.force_login(self.student)
        self.client.post(reverse("courses:enroll_click", args=[self.course_a.pk]))
        self.client.post(reverse("courses:enroll_click", args=[self.course_b.pk]))
        self.assertFalse(self.course_b.enrollments.filter(student=self.student).exists())

    def test_non_conflicting_course_can_be_enrolled(self):
        self.client.force_login(self.student)
        self.client.post(reverse("courses:enroll_click", args=[self.course_a.pk]))
        self.client.post(reverse("courses:enroll_click", args=[self.course_c.pk]))
        self.assertTrue(self.course_c.enrollments.filter(student=self.student).exists())

    def test_professor_cannot_enroll(self):
        self.client.force_login(self.professor)
        response = self.client.post(reverse("courses:enroll_click", args=[self.course_a.pk]))
        self.assertEqual(response.status_code, 403)
