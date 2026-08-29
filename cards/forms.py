from django import forms
from .models import KnowledgeCard


class KnowledgeCardUploadForm(forms.ModelForm):
    class Meta:
        model = KnowledgeCard
        fields = ["language", "source_media"]