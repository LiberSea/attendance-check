from django import forms


class CheckInForm(forms.Form):
    code = forms.CharField(label="출석 코드", max_length=6)
