from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse
from django.utils.safestring import mark_safe

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from pages.models import TAProfile


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = [
    "email",
    "username",
    "is_staff",
    ]
    fieldsets = UserAdmin.fieldsets
    # Show email on the add form in addition to the defaults
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )

    # Inline to manage TA profile details (eligible courses, display name) from the user page
    class TAProfileInline(admin.StackedInline):
        model = TAProfile
        can_delete = False
        extra = 0
        filter_horizontal = ("eligible_courses",)
        readonly_fields = ("manage_availability",)
        fields = ("display_name", "eligible_courses", "manage_availability")

        def manage_availability(self, obj):
            if obj and obj.pk:
                url = reverse("admin:pages_taprofile_change", args=[obj.pk])
                return mark_safe(f'<a href="{url}">Manage availability (hours)</a>')
            return "Save the user first, then manage availability."

        manage_availability.short_description = "Hours"

    inlines = [TAProfileInline]
    
    
admin.site.register(CustomUser, CustomUserAdmin)