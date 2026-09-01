from django.urls import path

from . import views

app_name = "courses"

urlpatterns = [
    path("", views.course_list, name="list"),
    path("create/", views.course_create, name="create"),
    path("enroll/", views.enroll, name="enroll"),
    path("<int:pk>/", views.course_detail, name="detail"),
]
