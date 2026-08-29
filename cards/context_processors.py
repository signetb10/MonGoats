from .models import KnowledgeCard


def notifications(request):
    """Powers the header's Notifications dropdown on every page: the 5 most
    recently processed clips, so it's real pipeline output rather than a
    UI stub. Cheap enough to run per-request at hackathon scale (a handful
    of rows) - revisit with caching if the card table ever gets large.
    """
    recent_cards = KnowledgeCard.objects.order_by("-created_at")[:5]
    return {"notification_cards": recent_cards}
