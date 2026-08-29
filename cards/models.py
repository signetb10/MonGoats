from django.db import models


class KnowledgeCard(models.Model):
    LANGUAGE_CHOICES = [
        ("mn", "Mongolian"),
        ("ja", "Japanese"),
        ("ru", "Russian"),
    ]

    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)
    transcript = models.TextField()
    source_media = models.FileField(upload_to="cards/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_language_display()} card ({self.created_at:%Y-%m-%d %H:%M})"