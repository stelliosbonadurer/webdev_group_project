# pages/tests.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Course, TAProfile, Availability


class HomePageTests(TestCase):
    def test_url_exists_at_correct_location_homepageview(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        
        
    def test_homepage_view(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")
        self.assertContains(response, "Home")


class TAProfileEditTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="jane", email="jane@example.com", password="p4ssword!"
        )
        self.course1 = Course.objects.create(code="CS101", name="Intro")
        self.course2 = Course.objects.create(code="CS102", name="Data")

    def test_requires_login(self):
        response = self.client.get(reverse("ta_edit"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_update_courses_and_availability(self):
        self.client.login(username="jane", password="p4ssword!")

        # Management form for 1 availability row
        data = {
            # TAProfileForm fields
            "display_name": "Jane D.",
            "eligible_courses": [str(self.course1.pk), str(self.course2.pk)],
            # Inline formset management
            "availabilities-TOTAL_FORMS": "1",
            "availabilities-INITIAL_FORMS": "0",
            "availabilities-MIN_NUM_FORMS": "0",
            "availabilities-MAX_NUM_FORMS": "1000",
            # Row 0 fields
            "availabilities-0-day_of_week": "1",  # Tuesday
            "availabilities-0-start_time": "10:00",
            "availabilities-0-end_time": "11:00",
        }

        response = self.client.post(reverse("ta_edit"), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("home"))

        ta = TAProfile.objects.get(user=self.user)
        self.assertEqual(ta.display_name, "Jane D.")
        self.assertCountEqual(list(ta.eligible_courses.all()), [self.course1, self.course2])
        av = ta.availabilities.get()
        self.assertEqual(av.day_of_week, 1)
        self.assertEqual(str(av.start_time), "10:00:00")
        self.assertEqual(str(av.end_time), "11:00:00")

    def test_reject_overlapping_availability(self):
        self.client.login(username="jane", password="p4ssword!")

        data = {
            "display_name": "Jane",
            "eligible_courses": [],
            "availabilities-TOTAL_FORMS": "2",
            "availabilities-INITIAL_FORMS": "0",
            "availabilities-MIN_NUM_FORMS": "0",
            "availabilities-MAX_NUM_FORMS": "1000",
            # Overlapping rows
            "availabilities-0-day_of_week": "3",  # Thursday
            "availabilities-0-start_time": "09:00",
            "availabilities-0-end_time": "11:00",
            "availabilities-1-day_of_week": "3",
            "availabilities-1-start_time": "10:30",
            "availabilities-1-end_time": "12:00",
        }

        response = self.client.post(reverse("ta_edit"), data)
        # Should re-render with errors
        self.assertEqual(response.status_code, 200)
        # Check that a validation error is displayed (overlap error on formset)
        self.assertContains(response, "overlap")
        ta = TAProfile.objects.get(user=self.user)
        self.assertEqual(ta.availabilities.count(), 0)