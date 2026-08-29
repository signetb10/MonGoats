from django.shortcuts import get_object_or_404, redirect, render

from .forms import KnowledgeCardUploadForm
from .models import KnowledgeCard
from .services import create_knowledge_card


def home_view(request):
    """Landing page: hero with the floating-greeting animation, plus the
    swipeable story feed built straight from whatever the upload pipeline
    has produced so far."""
    cards = KnowledgeCard.objects.select_related("owner").all()[:30]
    return render(request, "home.html", {"cards": cards})


def about_view(request):
    return render(request, "about.html")


def upload_view(request):
    if request.method == "POST":
        form = KnowledgeCardUploadForm(request.POST, request.FILES)
        if form.is_valid():
            card = create_knowledge_card(
                uploaded_file=form.cleaned_data["source_media"],
                language_code=form.cleaned_data["language"],
                owner=request.user,
            )
            return redirect("card_detail", pk=card.pk)
    else:
        form = KnowledgeCardUploadForm()
    return render(request, "cards/upload.html", {"form": form})


def card_detail_view(request, pk):
    card = get_object_or_404(KnowledgeCard, pk=pk)
    return render(request, "cards/card_detail.html", {"card": card})
