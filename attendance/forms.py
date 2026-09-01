from django import forms


class CheckInForm(forms.Form):
    code = forms.CharField(label="출석 코드", max_length=6)


class SessionOpenForm(forms.Form):
    duration_minutes = forms.IntegerField(
        label="세션 진행 시간(분)", min_value=1, initial=15,
        help_text="이 시간이 지나면 세션이 자동으로 마감됩니다.",
    )
    late_after_minutes = forms.IntegerField(
        label="지각 처리 기준(분)", min_value=0, initial=5,
        help_text="세션 시작 후 이 시간이 지나 체크인하면 지각으로 처리됩니다.",
    )

    def clean(self):
        cleaned_data = super().clean()
        duration = cleaned_data.get("duration_minutes")
        late_after = cleaned_data.get("late_after_minutes")
        if duration is not None and late_after is not None and late_after > duration:
            self.add_error("late_after_minutes", "지각 기준 시간은 세션 진행 시간보다 클 수 없습니다.")
        return cleaned_data
