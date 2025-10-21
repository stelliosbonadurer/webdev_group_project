from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q, F

# Create your models here.

#Course model
class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    
    class Meta:
        ordering = ["code"]
        
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    
#TA Profile model
class TAProfile(models.Model):
    #Each TA will be a single user
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ta_profile",
    )
    # Optional display name to show publicly instead of username
    display_name = models.CharField(max_length=100, blank=True)
    #Each TA can have multiple courses and visa versa
    eligible_courses = models.ManyToManyField(
        Course, related_name="eligible_tas", blank=True
    )
    
#Availability model, each TA will have an availability model.
class Availability(models.Model):
    class DayOfWeek(models.IntegerChoices):
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"
    
    ta = models.ForeignKey(
        TAProfile, on_delete=models.CASCADE, related_name="availabilities"
    )
    day_of_week = models.IntegerField(choices=DayOfWeek.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    class Meta:
        ordering = ["ta", "day_of_week", "start_time"]
        constraints = [
            models.CheckConstraint(
                check=Q(end_time__gt=F("start_time")),
                name="availability_end_after_start",
            ),
        ]
        unique_together = ("ta", "day_of_week", "start_time", "end_time")
        
    def clean(self):
        super().clean()
        # If any required time/day fields are missing (e.g., empty extra formset rows), skip validation.
        if self.start_time is None or self.end_time is None or self.day_of_week is None:
            return
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")
        # If TA isn't saved yet, skip overlap checks for now to avoid
        # "Model instances passed to related filters must be saved" during form validation.
        if not self.ta_id:
            return
        # Prevent overlaps on the same day for the same TA
        qs = Availability.objects.filter(ta=self.ta, day_of_week=self.day_of_week)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.filter(Q(start_time__lt=self.end_time) & Q(end_time__gt=self.start_time)).exists():
            raise ValidationError("This availability overlaps an existing time window.")

    def __str__(self):
        return f"{self.get_day_of_week_display()} {self.start_time}-{self.end_time} for {self.ta}"