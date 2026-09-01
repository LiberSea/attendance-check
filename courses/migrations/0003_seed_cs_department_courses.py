import datetime

from django.db import migrations


CS_COURSES = [
    ("이산수학", "CE-101", "mon", "09:00", "10:00", "공학관 301"),
    ("자료구조", "CE-201", "mon", "10:00", "11:00", "공학관 401"),
    ("알고리즘", "CE-301", "mon", "13:00", "15:00", "공학관 402"),
    ("컴퓨터구조", "CE-202", "tue", "09:00", "10:00", "공학관 401"),
    ("운영체제", "CE-302", "tue", "13:00", "15:00", "공학관 403"),
    ("데이터베이스", "CE-303", "wed", "09:00", "11:00", "공학관 401"),
    ("컴퓨터네트워크", "CE-304", "wed", "13:00", "14:00", "공학관 404"),
    ("소프트웨어공학", "CE-305", "thu", "10:00", "12:00", "공학관 402"),
    ("인공지능", "CE-401", "thu", "14:00", "16:00", "공학관 405"),
    ("웹프로그래밍", "CE-306", "fri", "09:00", "11:00", "공학관 403"),
]


def parse_time(value):
    hour, minute = value.split(":")
    return datetime.time(int(hour), int(minute))


def seed_courses(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    Course = apps.get_model("courses", "Course")

    professor, _ = User.objects.get_or_create(
        username="cs_dept",
        defaults={
            "email": "cs_dept@example.edu",
            "role": "professor",
            "first_name": "컴퓨터공학과",
            "is_active": True,
            "password": "!unusable",
        },
    )

    for name, code, day, start, end, classroom in CS_COURSES:
        Course.objects.get_or_create(
            code=code,
            defaults={
                "name": name,
                "professor": professor,
                "day_of_week": day,
                "start_time": parse_time(start),
                "end_time": parse_time(end),
                "classroom": classroom,
            },
        )


def remove_seeded_courses(apps, schema_editor):
    Course = apps.get_model("courses", "Course")
    Course.objects.filter(code__in=[code for _, code, *_ in CS_COURSES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0002_course_classroom_course_day_of_week_course_end_time_and_more"),
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_courses, remove_seeded_courses),
    ]
