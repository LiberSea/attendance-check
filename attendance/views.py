import csv

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import User
from courses.models import Course

from .forms import CheckInForm
from .models import AttendanceRecord, AttendanceSession


def _is_course_owner(user, course):
    return user.role == User.Role.PROFESSOR and course.professor_id == user.id


def _is_enrolled(user, course):
    return course.enrollments.filter(student=user).exists()


@login_required
def course_sessions(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    is_owner = _is_course_owner(request.user, course)
    is_enrolled = _is_enrolled(request.user, course)
    if not is_owner and not is_enrolled:
        return HttpResponseForbidden("이 강의의 출석 정보를 볼 권한이 없습니다.")

    sessions = course.sessions.all()

    if is_owner:
        return render(
            request,
            "attendance/session_list_professor.html",
            {"course": course, "sessions": sessions},
        )

    my_records = {
        record.session_id: record
        for record in AttendanceRecord.objects.filter(session__course=course, student=request.user)
    }
    rows = [(session, my_records.get(session.id)) for session in sessions]
    return render(
        request,
        "attendance/session_list_student.html",
        {"course": course, "rows": rows},
    )


@login_required
def session_open(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    if not _is_course_owner(request.user, course):
        return HttpResponseForbidden("교수만 출석 세션을 열 수 있습니다.")

    if request.method == "POST":
        session = AttendanceSession.objects.create(course=course, date=timezone.localdate())
        return redirect("attendance:session_detail", pk=session.pk)

    return redirect("attendance:course_sessions", course_pk=course.pk)


@login_required
def session_detail(request, pk):
    session = get_object_or_404(AttendanceSession, pk=pk)
    course = session.course
    is_owner = _is_course_owner(request.user, course)
    is_enrolled = _is_enrolled(request.user, course)
    if not is_owner and not is_enrolled:
        return HttpResponseForbidden("이 출석 세션에 접근할 권한이 없습니다.")

    if is_owner:
        records = session.records.select_related("student")
        return render(
            request,
            "attendance/session_detail_professor.html",
            {"session": session, "course": course, "records": records},
        )

    my_record = session.records.filter(student=request.user).first()
    return render(
        request,
        "attendance/session_detail_student.html",
        {"session": session, "course": course, "my_record": my_record},
    )


@login_required
def session_close(request, pk):
    session = get_object_or_404(AttendanceSession, pk=pk)
    course = session.course
    if not _is_course_owner(request.user, course):
        return HttpResponseForbidden("교수만 출석 세션을 마감할 수 있습니다.")

    if request.method == "POST" and session.is_open:
        session.closed_at = timezone.now()
        session.save(update_fields=["closed_at"])

        enrolled_ids = set(course.enrollments.values_list("student_id", flat=True))
        recorded_ids = set(session.records.values_list("student_id", flat=True))
        missing_ids = enrolled_ids - recorded_ids
        AttendanceRecord.objects.bulk_create(
            [
                AttendanceRecord(session=session, student_id=student_id, status=AttendanceRecord.Status.ABSENT)
                for student_id in missing_ids
            ]
        )

    return redirect("attendance:session_detail", pk=pk)


@login_required
def check_in(request, pk):
    session = get_object_or_404(AttendanceSession, pk=pk)
    course = session.course
    if request.user.role != User.Role.STUDENT or not _is_enrolled(request.user, course):
        return HttpResponseForbidden("수강생만 출석 체크를 할 수 있습니다.")

    if request.method == "POST":
        form = CheckInForm(request.POST)
        if form.is_valid():
            if not session.is_open:
                form.add_error(None, "마감된 출석 세션입니다.")
            elif form.cleaned_data["code"].strip().upper() != session.code:
                form.add_error("code", "출석 코드가 일치하지 않습니다.")
            else:
                AttendanceRecord.objects.update_or_create(
                    session=session,
                    student=request.user,
                    defaults={"status": AttendanceRecord.Status.PRESENT, "checked_at": timezone.now()},
                )
                return redirect("attendance:session_detail", pk=pk)
    else:
        form = CheckInForm()

    return render(request, "attendance/check_in.html", {"form": form, "session": session, "course": course})


@login_required
def course_stats(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    if not _is_course_owner(request.user, course):
        return HttpResponseForbidden("교수만 출석 통계를 볼 수 있습니다.")

    total_sessions = course.sessions.filter(closed_at__isnull=False).count()
    rows = []
    for enrollment in course.enrollments.select_related("student"):
        student = enrollment.student
        records = AttendanceRecord.objects.filter(session__course=course, student=student)
        present = records.filter(status=AttendanceRecord.Status.PRESENT).count()
        late = records.filter(status=AttendanceRecord.Status.LATE).count()
        absent = records.filter(status=AttendanceRecord.Status.ABSENT).count()
        rate = round((present + late) / total_sessions * 100, 1) if total_sessions else None
        rows.append(
            {"student": student, "present": present, "late": late, "absent": absent, "rate": rate}
        )

    return render(
        request,
        "attendance/course_stats.html",
        {"course": course, "rows": rows, "total_sessions": total_sessions},
    )


@login_required
def export_csv(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    if not _is_course_owner(request.user, course):
        return HttpResponseForbidden("교수만 내보내기를 할 수 있습니다.")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{course.code}_attendance.csv"'
    response.write("﻿")

    writer = csv.writer(response)
    writer.writerow(["날짜", "학번", "이름", "상태", "체크시각"])

    records = (
        AttendanceRecord.objects.filter(session__course=course)
        .select_related("student", "session")
        .order_by("session__date", "student__student_id")
    )
    for record in records:
        writer.writerow(
            [
                record.session.date,
                record.student.student_id,
                record.student.username,
                record.get_status_display(),
                record.checked_at or "",
            ]
        )
    return response
