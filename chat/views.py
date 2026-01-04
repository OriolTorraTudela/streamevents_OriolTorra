from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.utils.timezone import localtime


from events.models import Event
from .forms import ChatMessageForm
from .models import ChatMessage


MAX_MESSAGES = 50


def _json_error(message: str, *, status: int = 400) -> JsonResponse:
    return JsonResponse({"success": False, "error": message}, status=status)


def _json_form_errors(form, *, status: int = 400) -> JsonResponse:
    return JsonResponse({"success": False, "errors": form.errors}, status=status)


def _serialize_message(msg: ChatMessage, *, user_obj=None, viewer=None, event_creator_id=None) -> dict:
    username = ""
    display_name = ""

    if user_obj is not None:
        username = getattr(user_obj, "username", "") or ""
        display_name = getattr(user_obj, "display_name", None) or username
    else:
        # Fallback (pot tocar FK)
        username = getattr(getattr(msg, "user", None), "username", "") or ""
        display_name = msg.get_user_display_name()

    is_highlighted = bool(getattr(msg, "is_highlighted", False))

    # Permisos: si event_creator_id es passa, podem evitar tocar msg.event
    can_delete = False
    if viewer is not None and getattr(viewer, "is_authenticated", False):
        if getattr(viewer, "is_staff", False):
            can_delete = True
        elif getattr(viewer, "id", None) == getattr(msg, "user_id", None):
            can_delete = True
        elif event_creator_id is not None and getattr(viewer, "id", None) == event_creator_id:
            can_delete = True
        else:
            # Fallback (pot tocar FK)
            can_delete = msg.can_delete(viewer)

    return {
        "id": msg.pk,
        "user": username,
        "display_name": display_name,
        "message": msg.message,
        "created_at": msg.get_time_since(),
        "can_delete": can_delete,
        "is_highlighted": is_highlighted,
    }


@login_required
@require_POST
def chat_send_message(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)

    if not event.is_live:
        return JsonResponse(
            {"success": False, "errors": {"__all__": ["L'esdeveniment no està en directe."]}},
            status=400,
        )

    form = ChatMessageForm(request.POST)
    if not form.is_valid():
        return _json_form_errors(form, status=400)

    msg = form.save(commit=False)
    msg.user = request.user
    msg.event = event
    msg.save()

    return JsonResponse(
        {
            "success": True,
            "message": _serialize_message(
                msg,
                viewer=request.user,
                event_creator_id=event.creator_id,
            ),
        }
    )


def chat_load_messages(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)

    # Djongo-safe:
    msgs = list(ChatMessage.objects.filter(event_id=event_pk).order_by())

    # Soft delete en Python
    msgs = [m for m in msgs if not bool(getattr(m, "is_deleted", False))]

    # Ordenació en Python
    msgs.sort(key=lambda m: m.created_at)

    # Últims 50
    if len(msgs) > MAX_MESSAGES:
        msgs = msgs[-MAX_MESSAGES:]

    # Bulk users (evita tocar FK m.user)
    User = get_user_model()
    user_ids = [m.user_id for m in msgs if m.user_id]
    users_map = User.objects.in_bulk(user_ids)

    viewer = request.user
    viewer_id = getattr(viewer, "id", None)
    viewer_is_auth = getattr(viewer, "is_authenticated", False)
    viewer_is_staff = getattr(viewer, "is_staff", False)
    creator_id = event.creator_id

    payload = []
    for m in msgs:
        u = users_map.get(m.user_id)

        username = getattr(u, "username", "") if u else ""
        display_name = getattr(u, "display_name", None) if u else None
        if not display_name:
            display_name = username

        can_delete = False
        if viewer_is_auth:
            if viewer_is_staff or (viewer_id == m.user_id) or (viewer_id == creator_id):
                can_delete = True

        created = localtime(m.created_at).strftime("%d/%m/%Y %H:%M") if m.created_at else ""

        payload.append(
            {
                "id": m.pk,
                "user": username,
                "display_name": display_name,
                "message": m.message,
                "created_at": created,
                "can_delete": can_delete,
                "is_highlighted": bool(getattr(m, "is_highlighted", False)),
            }
        )

    return JsonResponse({"messages": payload})


@login_required
@require_POST
def chat_delete_message(request, message_pk):
    msg = get_object_or_404(ChatMessage, pk=message_pk)

    if not msg.can_delete(request.user):
        return _json_error("No tens permís per eliminar aquest missatge.", status=403)

    msg.is_deleted = True
    msg.save()
    return JsonResponse({"success": True})


@login_required
@require_POST
def chat_highlight_message(request, message_pk):
    msg = get_object_or_404(ChatMessage, pk=message_pk)

    # Evitem tocar msg.event si podem, però aquí és acceptable perquè és 1 objecte
    if msg.event.creator_id != request.user.id:
        return _json_error("No tens permís per destacar missatges.", status=403)

    msg.is_highlighted = not msg.is_highlighted
    msg.save()
    return JsonResponse({"success": True, "is_highlighted": msg.is_highlighted})
