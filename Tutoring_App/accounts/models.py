# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    @property
    def is_ta(self) -> bool:
        """Return True if this user has an associated TAProfile."""
        return hasattr(self, "ta_profile")