from django.shortcuts import render, redirect

from .forms import KnowledgeCardUploadForm
from .services import create_knowledge_card


def upload_view(request):
    if request.method == "POST":
        form = KnowledgeCardUploadForm(request.POST, request.FILES)
        if form.is_valid():
            card = create_knowledge_card(
                uploaded_file=form.cleaned_data["source_media"],
                language_code=form.cleaned_data["language"],
            )
            return redirect("card_detail", pk=card.pk)
    else:
        form = KnowledgeCardUploadForm()
    return render(request, "cards/upload.html", {"form": form})
