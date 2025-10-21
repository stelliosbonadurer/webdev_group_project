# accounts/views.py
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.shortcuts import redirect
from django.db import transaction
from django.core.exceptions import ValidationError

from .forms import CustomUserCreationForm
from pages.forms import TAProfileForm, AvailabilityInlineFormSet
from pages.models import TAProfile


class SignUpView(CreateView):
    """Create a user and capture TA details (eligible courses + availability).

    This keeps the class-based view while orchestrating extra forms in get/post.
    """

    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # TA courses form
        if "ta_form" not in context:
            context["ta_form"] = TAProfileForm(self.request.POST or None)

        # Availability formset bound to a temporary unsaved TAProfile for rendering/validation
        if "availability_formset" not in context:
            context["availability_formset"] = AvailabilityInlineFormSet(
                self.request.POST or None, instance=TAProfile()
            )

        return context

    def post(self, request, *args, **kwargs):
        # Primary user form from CreateView
        self.object = None
        user_form = self.get_form()
        ta_form = TAProfileForm(request.POST)

        # Build a display-only formset for re-rendering when user/ta form invalid
        availability_formset_display = AvailabilityInlineFormSet(request.POST, instance=TAProfile())

        # First validate user + TA forms
        if not (user_form.is_valid() and ta_form.is_valid()):
            return self.render_to_response(
                self.get_context_data(
                    form=user_form,
                    ta_form=ta_form,
                    availability_formset=availability_formset_display,
                )
            )

        # Now validate availability formset bound to a real saved TAProfile.
        with transaction.atomic():
            # Save user and TA profile inside a savepoint so we can roll back if availability is invalid
            sid = transaction.savepoint()
            user = user_form.save()
            ta_profile = TAProfile.objects.create(user=user)
            # Set display_name and courses from TA form
            ta_profile.display_name = ta_form.cleaned_data.get("display_name", "")
            ta_profile.save()
            courses = ta_form.cleaned_data.get("eligible_courses") or []
            ta_profile.eligible_courses.set(courses)

            # Gracefully handle the case where no availability formset data was submitted.
            # If the management form keys are missing, treat it as an empty, valid submission.
            temp_empty_fs = AvailabilityInlineFormSet(instance=ta_profile)
            mgmt_prefix = f"{temp_empty_fs.prefix}-TOTAL_FORMS"
            if mgmt_prefix not in request.POST:
                # No availability provided; commit user + TA profile and redirect
                self.object = user
                return redirect(self.get_success_url())

            # Management data is present; validate the bound formset
            bound_formset = AvailabilityInlineFormSet(request.POST, instance=ta_profile)
            if bound_formset.is_valid():
                bound_formset.save()
                # Ensure CreateView's success_url formatting has self.object available
                self.object = user
                return redirect(self.get_success_url())
            # Rollback creation of user and TAProfile so we don't leave partial data
            transaction.savepoint_rollback(sid)
            # Re-render with the bound formset errors collected
            return self.render_to_response(
                self.get_context_data(
                    form=user_form,
                    ta_form=ta_form,
                    availability_formset=bound_formset,
                )
            )