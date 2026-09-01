from django import forms

from .models import Course


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["name", "code"]
        labels = {"name": "강의명", "code": "강의 코드"}


class EnrollForm(forms.Form):
    code = forms.CharField(label="강의 코드", max_length=20)
