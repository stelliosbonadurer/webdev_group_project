from django import forms
from django.forms import inlineformset_factory
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

AvailabilityInlineFormSet = inlineformset_factory(
    TAProfile,
    Availability,
    fields=("day_of_week", "start_time", "end_time"),
    extra=2,
    can_delete=True,
    widgets={
        "start_time": forms.TimeInput(format="%H:%M", attrs={"type": "time"}),
        "end_time": forms.TimeInput(format="%H:%M", attrs={"type": "time"}),
    },
)