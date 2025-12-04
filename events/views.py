from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import DatabaseError
from django.http import Http404, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator

from events.models import Event, CATEGORY_CHOICES
from .forms import EventCreationForm, EventUpdateForm, EventSearchForm


# ==========================
#   HELPERS GENERALS
# ==========================

def _safe_list(queryset, request, error_message):
    """
    Converteix un queryset en llista atrapant DatabaseError.
    Retorna sempre una llista (pot ser buida).
    """
    try:
        return list(queryset)
    except DatabaseError:
        messages.error(request, error_message)
        return []


def _filter_and_sort_events(events, form):
    """
    Aplica filtres i ordenació en memòria sobre una llista d'events.
    - Cerca per títol/descr
    - Filtre categoria, estat, etiquetes, dates
    - Ordenació: destacats primer, després created_at desc
    """
    if not form.is_valid():
        filtered = events
    else:
        cleaned = form.cleaned_data

        search = (cleaned.get("search") or "").strip().lower()
        category = cleaned.get("category") or ""
        status = cleaned.get("status") or ""
        tag = (cleaned.get("tag") or "").strip().lower()
        date_from = cleaned.get("date_from")
        date_to = cleaned.get("date_to")

        filtered = []
        for e in events:
            ok = True

            # Cerca per títol o descripció
            if search:
                title = (e.title or "").lower()
                desc = (e.description or "").lower()
                if search not in title and search not in desc:
                    ok = False

            # Categoria
            if ok and category and e.category != category:
                ok = False

            # Estat
            if ok and status and e.status != status:
                ok = False

            # Etiqueta
            if ok and tag:
                tags_lower = [t.lower() for t in e.get_tags_list()]
                if tag not in tags_lower:
                    ok = False

            # Dates (comparems per .date())
            if ok and date_from:
                if not e.scheduled_date or e.scheduled_date.date() < date_from:
                    ok = False

            if ok and date_to:
                if not e.scheduled_date or e.scheduled_date.date() > date_to:
                    ok = False

            if ok:
                filtered.append(e)

    # Ordenació: destacats primer, després per created_at desc
    def sort_key(ev):
        created_ts = 0
        if getattr(ev, "created_at", None):
            created_ts = ev.created_at.timestamp()
        # (0, -ts) per destacats, (1, -ts) per la resta
        return (0 if getattr(ev, "is_featured", False) else 1, -created_ts)

    filtered.sort(key=sort_key)
    return filtered


def _safe_get_event_or_redirect(request, pk, redirect_name, error_message):
    """
    Helper per obtenir un event o redirigir amb missatge d'error.
    """
    try:
        event = get_object_or_404(Event, pk=pk)
    except DatabaseError:
        messages.error(request, error_message)
        return None, redirect(redirect_name)
    return event, None


# ==========================
#   VISTES
# ==========================

def event_list_view(request):
    """
    Llistat d'esdeveniments:
    - Una sola consulta simple a la BD (Event.objects.all())
    - Filtres, cerca i ordenació en memòria per evitar problemes amb Djongo
    - Paginació: 12 elements per pàgina
    """
    form = EventSearchForm(request.GET or None)

    events = _safe_list(
        Event.objects.all(),
        request,
        "S'ha produït un error accedint als esdeveniments a la base de dades.",
    )

    # Filtres + ordenació
    events = _filter_and_sort_events(events, form)

    # Tag cloud 
    tag_cloud = Event.get_tag_cloud(limit=30)

    # Paginació
    paginator = Paginator(events, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "form": form,
        "page_obj": page_obj,
        "events": page_obj.object_list,
        "tag_cloud": tag_cloud,
    }
    return render(request, "events/event_list.html", context)


def event_detail_view(request, pk):
    """
    Detall d'esdeveniment.
    """
    event, redirect_response = _safe_get_event_or_redirect(
        request,
        pk,
        "events:event_list",
        "No s'ha pogut carregar aquest esdeveniment per un error de base de dades.",
    )
    if redirect_response:
        return redirect_response

    is_creator = request.user.is_authenticated and event.creator == request.user

    context = {
        "event": event,
        "is_creator": is_creator,
    }
    return render(request, "events/event_detail.html", context)


@login_required
def event_create_view(request):
    """
    Crear esdeveniment.
    """
    if request.method == "POST":
        form = EventCreationForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            try:
                event = form.save(commit=False)
                event.creator = request.user
                event.save()
            except DatabaseError:
                messages.error(
                    request,
                    "No s'ha pogut desar l'esdeveniment per un error de base de dades.",
                )
            else:
                messages.success(request, "Esdeveniment creat correctament.")
                return redirect(event.get_absolute_url())
    else:
        form = EventCreationForm(user=request.user)

    return render(
        request,
        "events/event_form.html",
        {"form": form, "mode": "create"},
    )


@login_required
def event_update_view(request, pk):
    """
    Editar esdeveniment.
    Només el creador pot editar.
    """
    event, redirect_response = _safe_get_event_or_redirect(
        request,
        pk,
        "events:event_list",
        "No s'ha pogut carregar l'esdeveniment per editar-lo.",
    )
    if redirect_response:
        return redirect_response

    if event.creator != request.user:
        return HttpResponseForbidden("No tens permís per editar aquest esdeveniment.")

    if request.method == "POST":
        form = EventUpdateForm(
            request.POST,
            request.FILES,
            instance=event,
            user=request.user,
        )
        if form.is_valid():
            try:
                form.save()
            except DatabaseError:
                messages.error(
                    request,
                    "No s'han pogut desar els canvis per un error de base de dades.",
                )
            else:
                messages.success(request, "Esdeveniment actualitzat correctament.")
                return redirect(event.get_absolute_url())
    else:
        form = EventUpdateForm(instance=event, user=request.user)

    return render(
        request,
        "events/event_form.html",
        {"form": form, "mode": "update", "event": event},
    )


@login_required
def event_delete_view(request, pk):
    """
    Eliminar esdeveniment.
    Només creador + confirmació.
    """
    event, redirect_response = _safe_get_event_or_redirect(
        request,
        pk,
        "events:event_list",
        "No s'ha pogut carregar l'esdeveniment per eliminar-lo.",
    )
    if redirect_response:
        return redirect_response

    if event.creator != request.user:
        return HttpResponseForbidden("No tens permís per eliminar aquest esdeveniment.")

    if request.method == "POST":
        try:
            event.delete()
        except DatabaseError:
            messages.error(
                request,
                "No s'ha pogut eliminar l'esdeveniment per un error de base de dades.",
            )
        else:
            messages.success(request, "Esdeveniment eliminat correctament.")
        return redirect("events:event_list")

    return render(request, "events/event_confirm_delete.html", {"event": event})


@login_required
def my_events_view(request):
    """
    Esdeveniments de l'usuari actual.
    """
    status_filter = request.GET.get("status") or ""

    all_events = _safe_list(
        Event.objects.filter(creator=request.user),
        request,
        "No s'han pogut carregar els teus esdeveniments per un error de base de dades.",
    )

    stats = {
        "total": len(all_events),
        "scheduled": sum(1 for e in all_events if e.status == "scheduled"),
        "live": sum(1 for e in all_events if e.status == "live"),
        "finished": sum(1 for e in all_events if e.status == "finished"),
        "cancelled": sum(1 for e in all_events if e.status == "cancelled"),
    }

    if status_filter:
        events = [e for e in all_events if e.status == status_filter]
    else:
        events = all_events

    context = {
        "events": events,
        "status_filter": status_filter,
        "stats": stats,
    }
    return render(request, "events/my_events.html", context)


def events_by_category_view(request, category):
    """
    Esdeveniments per categoria amb paginació.
    """
    valid_categories = [c[0] for c in CATEGORY_CHOICES]
    if category not in valid_categories:
        raise Http404("Categoria inexistent.")

    events = _safe_list(
        Event.objects.filter(category=category),
        request,
        "No s'han pogut carregar els esdeveniments d'aquesta categoria.",
    )

    events = _filter_and_sort_events(events, EventSearchForm())

    paginator = Paginator(events, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "events": page_obj.object_list,
        "page_obj": page_obj,
        "category": category,
    }
    return render(request, "events/event_list.html", context)


def tags_autocomplete_view(request):
    """
    Endpoint d'autocompletar etiquetes.
    Retorna JSON amb una llista de tags que comencen pel prefix 'q'.
    """
    q = (request.GET.get("q") or "").strip()
    suggestions = Event.search_tags(q, limit=10)
    return JsonResponse({"results": suggestions})
