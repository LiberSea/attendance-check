from django.urls import path

from . import views

app_name = "attendance"

urlpatterns = [
    path("course/<int:course_pk>/sessions/", views.course_sessions, name="course_sessions"),
    path("course/<int:course_pk>/sessions/open/", views.session_open, name="session_open"),
    path("course/<int:course_pk>/stats/", views.course_stats, name="course_stats"),
    path("course/<int:course_pk>/export/", views.export_csv, name="export_csv"),
    path("session/<int:pk>/", views.session_detail, name="session_detail"),
    path("session/<int:pk>/qr/", views.session_qr, name="session_qr"),
    path("session/<int:pk>/close/", views.session_close, name="session_close"),
    path("session/<int:pk>/check-in/", views.check_in, name="check_in"),
]
