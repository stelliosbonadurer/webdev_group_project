from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser


# NOTE: Keep a single, clear definition of the custom user forms.
# These forms extend Django's built-ins and add the extra "age" field.

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        # password1/password2 are declared directly on UserCreationForm,
        # so they will be included automatically.
        fields = ("username", "email", "age")


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        # Limit to commonly edited fields; admin fieldsets control the rest.
        fields = ("username", "email", "age")