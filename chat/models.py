from django.db import models
from djongo import models
from django.conf import settings
from django.utils.timesince import timesince

from events.models import Event


class ChatMessage(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    message = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    # Soft delete
    is_deleted = models.BooleanField(default=False)

    # Bonus: highlight
    is_highlighted = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]  # més antic primer
        verbose_name = "Missatge de Xat"
        verbose_name_plural = "Missatges de Xat"

    def __str__(self) -> str:
        preview = (self.message or "")[:50]
        return f"{self.user.username}: {preview}"

    def can_delete(self, user) -> bool:
        if not user or not getattr(user, "is_authenticated", False):
            return False
        if getattr(user, "is_staff", False):
            return True
        if self.user_id == user.id:
            return True
        # Creador de l'esdeveniment
        if self.event and getattr(self.event, "creator_id", None) == user.id:
            return True
        return False

    def get_user_display_name(self) -> str:
        # CustomUser: display_name pot existir
        dn = getattr(self.user, "display_name", None)
        if dn:
            return dn
        return self.user.username

    def get_time_since(self) -> str:
        # Format “fa X …”
        return f"fa {timesince(self.created_at)}"
