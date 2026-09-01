from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User

from .forms import CourseForm, EnrollForm
from .models import Course, Enrollment


@login_required
def course_list(request):
    if request.user.role == User.Role.PROFESSOR:
        courses = Course.objects.filter(professor=request.user)
    else:
        courses = Course.objects.filter(enrollments__student=request.user)
    return render(request, "courses/course_list.html", {"courses": courses})


@login_required
def course_create(request):
    if request.user.role != User.Role.PROFESSOR:
        return HttpResponseForbidden("교수만 강의를 개설할 수 있습니다.")

    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.professor = request.user
            course.save()
            return redirect("courses:detail", pk=course.pk)
    else:
        form = CourseForm()
    return render(request, "courses/course_form.html", {"form": form})


@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)

    is_owner = request.user.role == User.Role.PROFESSOR and course.professor_id == request.user.id
    is_enrolled = course.enrollments.filter(student=request.user).exists()
    if not is_owner and not is_enrolled:
        return HttpResponseForbidden("이 강의에 접근할 권한이 없습니다.")

    enrollments = course.enrollments.select_related("student")
    return render(
        request,
        "courses/course_detail.html",
        {"course": course, "enrollments": enrollments, "is_owner": is_owner},
    )


@login_required
def enroll(request):
    if request.user.role != User.Role.STUDENT:
        return HttpResponseForbidden("학생만 수강신청을 할 수 있습니다.")

    if request.method == "POST":
        form = EnrollForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]
            course = Course.objects.filter(code=code).first()
            if course is None:
                form.add_error("code", "해당 강의 코드를 찾을 수 없습니다.")
            else:
                Enrollment.objects.get_or_create(student=request.user, course=course)
                return redirect("courses:detail", pk=course.pk)
    else:
        form = EnrollForm()
    return render(request, "courses/enroll.html", {"form": form})


DAY_ORDER = [Course.Day.MON, Course.Day.TUE, Course.Day.WED, Course.Day.THU, Course.Day.FRI]
PERIOD_START_HOUR = 9
PERIOD_END_HOUR = 18


@login_required
def timetable(request):
    courses = (
        Course.objects.exclude(day_of_week__isnull=True)
        .exclude(start_time__isnull=True)
        .exclude(end_time__isnull=True)
        .select_related("professor")
        .order_by("start_time")
    )

    my_course_ids = set()
    my_courses = []
    if request.user.role == User.Role.STUDENT:
        my_courses = list(
            Course.objects.filter(enrollments__student=request.user).exclude(day_of_week__isnull=True)
        )
        my_course_ids = {c.id for c in my_courses}

    blocks = []
    for course in courses:
        is_mine = course.id in my_course_ids
        has_conflict = False
        if request.user.role == User.Role.STUDENT and not is_mine:
            has_conflict = any(course.overlaps(mine) for mine in my_courses)
        blocks.append(
            {
                "course": course,
                "day_index": DAY_ORDER.index(course.day_of_week),
                "start_hour": course.start_time.hour,
                "span": max(course.end_time.hour - course.start_time.hour, 1),
                "is_mine": is_mine,
                "has_conflict": has_conflict,
            }
        )

    return render(
        request,
        "courses/timetable.html",
        {
            "blocks": blocks,
            "periods": range(PERIOD_START_HOUR, PERIOD_END_HOUR),
            "days": Course.Day.choices,
        },
    )


@login_required
def enroll_click(request, pk):
    if request.user.role != User.Role.STUDENT:
        return HttpResponseForbidden("학생만 수강신청을 할 수 있습니다.")

    course = get_object_or_404(Course, pk=pk)

    if request.method == "POST":
        already_enrolled = course.enrollments.filter(student=request.user).exists()
        if not already_enrolled:
            my_courses = Course.objects.filter(enrollments__student=request.user).exclude(day_of_week__isnull=True)
            if not any(course.overlaps(mine) for mine in my_courses):
                Enrollment.objects.get_or_create(student=request.user, course=course)

    return redirect("courses:timetable")
