from django.urls import path

from . import views

app_name = "courses"

urlpatterns = [
    path("", views.course_list, name="list"),
    path("create/", views.course_create, name="create"),
    path("enroll/", views.enroll, name="enroll"),
    path("timetable/", views.timetable, name="timetable"),
    path("<int:pk>/enroll/", views.enroll_click, name="enroll_click"),
    path("<int:pk>/", views.course_detail, name="detail"),
]
