from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import KnowledgeCardUploadForm
from .models import KnowledgeCard
from .services import create_knowledge_card


def home_view(request):
    query = request.GET.get("q", "").strip()
    cards = KnowledgeCard.objects.select_related("owner").all()

    if query:
        cards = cards.filter(
            Q(title__icontains=query)
            | Q(summary__icontains=query)
            | Q(transcript__icontains=query)
            | Q(translation__icontains=query)
        )

    return render(request, "home.html", {"cards": cards[:30], "query": query})

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
