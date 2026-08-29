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
    translation = models.TextField(blank=True, default="")
    title = models.CharField(max_length=200, blank=True, default="")
    summary = models.TextField(blank=True, default="")
    key_points = models.JSONField(blank=True, default=list)

    @property
    def is_video(self) -> bool:
        if not self.source_media:
            return False
        return self.source_media.name.lower().endswith((".mp4", ".mov"))

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_language_display()} card ({self.created_at:%Y-%m-%d %H:%M})"