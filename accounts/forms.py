from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class SignUpForm(UserCreationForm):
    """Django's UserCreationForm handles username + password validation and
    hashing for us; we only add the email field on top of it."""

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["bio", "avatar", "native_language"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4, "placeholder": "Tell the community a bit about yourself..."}),
        }


class ProfileUserForm(forms.ModelForm):
    """First-name/email edits live on the built-in User model, not Profile -
    split into its own form so ProfileForm above stays a clean 1:1 with the
    Profile model."""

    class Meta:
        model = User
        fields = ["first_name", "email"]
