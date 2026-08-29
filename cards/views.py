from .forms import KnowledgeCardUploadForm
from .services import create_knowledge_card
from django.shortcuts import get_object_or_404, render, redirect
from .models import KnowledgeCard


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

def card_detail_view(request, pk):
    card = get_object_or_404(KnowledgeCard, pk=pk)
    return render(request, "cards/card_detail.html", {"card": card})
