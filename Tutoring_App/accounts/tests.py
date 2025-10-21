# accounts/tests.py
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.contrib.admin.sites import site

from pages.models import TAProfile


class UsersManagersTests(TestCase):
	def test_create_user(self):
		User = get_user_model()
		user = User.objects.create_user(
			username="testuser",
			email="testuser@example.com",
			password="testpass1234",
		)
		self.assertEqual(user.username, "testuser")
		self.assertEqual(user.email, "testuser@example.com")
		self.assertTrue(user.is_active)
		self.assertFalse(user.is_staff)
		self.assertFalse(user.is_superuser)

	def test_create_superuser(self):
		User = get_user_model()
		admin_user = User.objects.create_superuser(
			username="testsuperuser",
			email="testsuperuser@example.com",
			password="testpass1234",
		)
		self.assertEqual(admin_user.username, "testsuperuser")
		self.assertEqual(admin_user.email, "testsuperuser@example.com")
		self.assertTrue(admin_user.is_active)
		self.assertTrue(admin_user.is_staff)
		self.assertTrue(admin_user.is_superuser)


class SignupPageTests(TestCase):
	def test_url_exists_at_correct_location_signupview(self):
		response = self.client.get("/accounts/signup/")
		self.assertEqual(response.status_code, 200)

	def test_signup_view_name(self):
		response = self.client.get(reverse("signup"))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, "registration/signup.html")

	def test_signup_form(self):
		response = self.client.post(
			reverse("signup"),
			{
				"username": "testuser",
				"email": "testuser@email.com",
				"password1": "testpass123",
				"password2": "testpass123",
			},
		)
		self.assertEqual(response.status_code, 302)
		self.assertEqual(get_user_model().objects.count(), 1)
		self.assertEqual(get_user_model().objects.first().username, "testuser")

	def test_signup_creates_ta_profile_without_availability(self):
		# Post minimal valid signup data (no availability submitted)
		response = self.client.post(
			reverse("signup"),
			{
				"username": "tauser",
				"email": "tauser@email.com",
				"password1": "testpass123",
				"password2": "testpass123",
			},
		)
		self.assertEqual(response.status_code, 302)
		user = get_user_model().objects.get(username="tauser")
		# TA profile is created and has no availabilities by default
		self.assertTrue(hasattr(user, "ta_profile"))
		self.assertEqual(user.ta_profile.availabilities.count(), 0)


class AdminRegistrationTests(TestCase):
	def test_customuser_registered_with_taprofile_inline(self):
		User = get_user_model()
		self.assertIn(User, site._registry)  # registered in admin
		admin_class = site._registry[User]
		# Inline classes are kept on the ModelAdmin subclass as 'inlines'
		inline_models = [getattr(inline, "model", None) for inline in getattr(admin_class, "inlines", [])]
		self.assertIn(TAProfile, inline_models)