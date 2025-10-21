# pages/views.py
from django.views.generic import TemplateView, View, DetailView
from django.db.models import Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.db import transaction

from .models import TAProfile, Availability, Course
from .forms import TAProfileForm, AvailabilityInlineFormSet


class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Prefetch courses and ordered availability for efficient rendering
        availability_qs = Availability.objects.order_by("day_of_week", "start_time")
        tas = (
            TAProfile.objects.select_related("user")
            .prefetch_related("eligible_courses", Prefetch("availabilities", queryset=availability_qs))
            .order_by("user__username")
        )
        context["tas"] = tas
        return context


class TAProfileEditView(LoginRequiredMixin, View):
    template_name = "pages/ta_edit.html"

    def get(self, request):
        ta_profile, _ = TAProfile.objects.get_or_create(user=request.user)
        ta_form = TAProfileForm(instance=ta_profile)
        availability_formset = AvailabilityInlineFormSet(instance=ta_profile)
        return render(
            request,
            self.template_name,
            {"ta_form": ta_form, "availability_formset": availability_formset},
        )

    def post(self, request):
        ta_profile, _ = TAProfile.objects.get_or_create(user=request.user)
        ta_form = TAProfileForm(request.POST, instance=ta_profile)
        availability_formset = AvailabilityInlineFormSet(request.POST, instance=ta_profile)
        if ta_form.is_valid() and availability_formset.is_valid():
            with transaction.atomic():
                ta_form.save()
                availability_formset.save()
            return redirect("home")
        return render(
            request,
            self.template_name,
            {"ta_form": ta_form, "availability_formset": availability_formset},
        )


class TAProfileDetailView(DetailView):
    model = TAProfile
    template_name = "pages/ta_view.html"
    context_object_name = "ta"

    def get_queryset(self):
        availability_qs = Availability.objects.order_by("day_of_week", "start_time")
        return (
            TAProfile.objects.select_related("user")
            .prefetch_related("eligible_courses", Prefetch("availabilities", queryset=availability_qs))
        )
