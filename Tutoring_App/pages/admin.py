from django.contrib import admin
from .models import Course, TAProfile, Availability


class AvailabilityInline(admin.TabularInline):
	model = Availability
	extra = 0


@admin.register(TAProfile)
class TAProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "display_name")
	search_fields = ("user__username", "user__email")
	filter_horizontal = ("eligible_courses",)
	inlines = [AvailabilityInline]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
	list_display = ("code", "name")
	search_fields = ("code", "name")


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
	list_display = ("ta", "day_of_week", "start_time", "end_time")
	list_filter = ("day_of_week", "ta")
