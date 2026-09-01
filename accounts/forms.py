from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=User.Role.choices, label="역할")
    student_id = forms.CharField(required=False, max_length=20, label="학번")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "role", "student_id")

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        student_id = cleaned_data.get("student_id")
        if role == User.Role.STUDENT and not student_id:
            self.add_error("student_id", "학생은 학번을 입력해야 합니다.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.role = self.cleaned_data["role"]
        user.student_id = self.cleaned_data["student_id"] if user.role == User.Role.STUDENT else None
        if commit:
            user.save()
        return user
