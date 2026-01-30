from django.shortcuts import render
from django.utils import timezone

from events.models import Event
from .services.embeddings import embed_text, model_name
from .services.ranker import cosine_top_k


def semantic_search(request):
    q = (request.GET.get("q") or "").strip()

    # Checkbox: si ve future=0 -> "not future", però el document el fa servir com "només futurs".
    # Implementació coherent amb el template del document:
    only_future = (request.GET.get("future", "1") == "0")

    results = []
    if q:
        q_vec = embed_text(q)

        qs = Event.objects.all()
        if only_future:
            qs = qs.filter(scheduled_date__gte=timezone.now())

        items = []
        for e in qs:
            items.append((e, getattr(e, "embedding", None)))

        results = cosine_top_k(q_vec, items, k=20)

    context = {
        "query": q,
        "results": results,  # [(Event, score)]
        "only_future": only_future,
        "embedding_model": model_name(),
    }
    return render(request, "semantic_search/search.html", context)
