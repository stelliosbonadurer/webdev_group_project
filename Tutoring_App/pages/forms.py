from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from django.core.exceptions import ValidationError
from .models import TAProfile, Availability, Course

class TAProfileForm(forms.ModelForm):
    display_name = forms.CharField(
        max_length=100,
        required=False,
        label="Display name",
        help_text="Optional name shown on the homepage (defaults to your username).",
    )
    eligible_courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Courses",
    )

    class Meta:
        model = TAProfile
        fields = ["display_name", "eligible_courses"]

class _AvailabilityFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        # Collect intervals per day and check for overlaps within the submission
        by_day = {}
        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue
            if form.cleaned_data.get("DELETE"):
                continue
            day = form.cleaned_data.get("day_of_week")
            start = form.cleaned_data.get("start_time")
            end = form.cleaned_data.get("end_time")
            if not (day is not None and start and end):
                # Incomplete rows are handled by field validators
                continue
            by_day.setdefault(day, []).append((start, end))

        for day, intervals in by_day.items():
            # sort by start and check end overlaps next start
            intervals.sort(key=lambda x: x[0])
            last_start, last_end = intervals[0]
            for cur_start, cur_end in intervals[1:]:
                if cur_start < last_end:
                    raise ValidationError("This availability overlaps an existing time window.")
                last_start, last_end = cur_start, cur_end


AvailabilityInlineFormSet = inlineformset_factory(
    TAProfile,
    Availability,
    fields=("day_of_week", "start_time", "end_time"),
    extra=2,
    can_delete=True,
    formset=_AvailabilityFormSet,
    widgets={
        "start_time": forms.TimeInput(format="%H:%M", attrs={"type": "time"}),
        "end_time": forms.TimeInput(format="%H:%M", attrs={"type": "time"}),
    },
)