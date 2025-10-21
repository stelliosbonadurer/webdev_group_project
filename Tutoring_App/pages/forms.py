from django import forms
from django.forms import inlineformset_factory
from .models import TAProfile, Availability, Course

class TAProfileForm(forms.ModelForm):
    eligible_courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Eligible courses",
    )

    class Meta:
        model = TAProfile
        fields = ["eligible_courses"]

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