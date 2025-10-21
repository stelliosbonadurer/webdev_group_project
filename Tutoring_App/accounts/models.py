# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    age = models.PositiveIntegerField(null=True, blank=True)

    @property
    def is_ta(self) -> bool:
        """Return True if this user has an associated TAProfile."""
        return hasattr(self, "ta_profile")