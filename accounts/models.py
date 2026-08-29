from django.conf import settings
from django.db import models


class Profile(models.Model):
    """One-to-one extension of Django's built-in User.

    We don't touch the auth_user table itself (that's Django's and it's
    battle-tested) - anything MonGoats-specific about a person lives here
    instead, so upgrading Django's auth internals later never risks this
    data.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    bio = models.TextField(blank=True, default="")
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    native_language = models.CharField(max_length=100, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile({self.user.username})"


def get_or_create_profile(user) -> Profile:
    """Callers should go through this rather than `user.profile` directly -
    accounts created before this app existed (or via the admin) won't have
    a Profile row yet, and this papers over that instead of 500ing.
    """
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile
