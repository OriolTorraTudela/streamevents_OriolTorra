from djongo import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from urllib.parse import urlparse, parse_qs
from collections import Counter
from io import BytesIO
import os

from django.core.files.base import ContentFile
from django.templatetags.static import static
from PIL import Image


# ==========================
#   CONSTANTS
# ==========================

CATEGORY_CHOICES = [
    ("Gaming", "Gaming"),
    ("Música", "Música"),
    ("Xerrades", "Xerrades"),
    ("Educació", "Educació"),
    ("Esports", "Esports"),
    ("Entreteniment", "Entreteniment"),
    ("Tecnologia", "Tecnologia"),
    ("Art i Creativitat", "Art i Creativitat"),
    ("Altres", "Altres"),
]

STATUS_CHOICES = [
    ("Programat", "Programat"),
    ("En Directe", "En Directe"),
    ("Finalitzat", "Finalitzat"),
    ("Cancel·lat", "Cancel·lat"),
]

CATEGORY_ESTIMATED_DURATION = {
    "Gaming": 180,          # 3 h
    "Música": 90,           # 1,5 h
    "Xerrades": 60,         # 1 h
    "Educació": 120,        # 2 h
    "Esports": 150,         # 2,5 h
    "Entreteniment": 120,   # 2 h
    "Tecnologia": 90,       # 1,5 h
    "Art i Creativitat": 120,  # 2 h
    "Altres": 90,           # 1,5 h
}


class Event(models.Model):
    # --- Camps bàsics ---
    title = models.CharField(
        max_length=200,
        help_text="Títol de l'esdeveniment",
    )
    description = models.TextField(
        help_text="Descripció detallada de l'esdeveniment",
    )

    # Creador (usuari que crea l'esdeveniment)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="events",
        on_delete=models.CASCADE,
    )

    # Categoria amb choices
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
    )

    # Data i hora programada
    scheduled_date = models.DateTimeField()

    # Estat amb choices
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="scheduled",
    )

    # Thumbnail opcional
    thumbnail = models.ImageField(
        upload_to="events/thumbnails/",
        blank=True,
        null=True,
    )

    # Nombre màxim d’espectadors
    max_viewers = models.PositiveIntegerField(default=100)

    # Destacat a la portada
    is_featured = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Tags com a string separada per comes
    tags = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Introdueix etiquetes separades per comes",
    )

    # URL del stream (YouTube, Twitch, etc.)
    stream_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="URL de YouTube, Twitch o similar",
    )

    class Meta:
        ordering = ["-created_at"]  # Més recents primer
        verbose_name = "Esdeveniment"
        verbose_name_plural = "Esdeveniments"

    # ---------- Mètodes bàsics ----------

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        """Retorna la URL del detall de l'esdeveniment."""
        return reverse("events:event_detail", args=[self.pk])

    # --- Propietats d'estat ---

    @property
    def is_live(self) -> bool:
        """Retorna True si l'esdeveniment està en directe."""
        return self.status == "live"

    @property
    def is_upcoming(self) -> bool:
        """
        Retorna True si està programat per al futur:
        - estat 'scheduled'
        - data posterior a ara
        """
        if not self.scheduled_date:
            return False
        return self.status == "scheduled" and self.scheduled_date > timezone.now()

    # --- Info derivada ---

    def get_duration(self) -> timedelta | None:
        """
        Calcula la durada estimada si l'esdeveniment està finalitzat.
        Torna un timedelta o None.
        """
        if self.status != "finished":
            return None

        minutes = CATEGORY_ESTIMATED_DURATION.get(self.category, 90)
        return timedelta(minutes=minutes)

    def get_tags_list(self) -> list[str]:
        """
        Retorna les etiquetes com a llista neta.
        Exemple: 'lol, gaming, esport' -> ['lol', 'gaming', 'esport']
        """
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(",") if tag.strip()]

    # --- Helpers per multimedia ---

    def get_stream_embed_url(self) -> str:
        """
        Converteix stream_url en una URL embed-friendly per a:
        - YouTube (vídeo i playlist)
        - Twitch (canal)

        Si no es reconeix el format, retorna la URL original.
        """
        if not self.stream_url:
            return ""

        url = self.stream_url.strip()
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()

        # ---------- YOUTUBE ----------
        if "youtube.com" in netloc:
            # Vídeo normal: https://www.youtube.com/watch?v=VIDEO_ID
            if parsed.path == "/watch":
                qs = parse_qs(parsed.query)
                video_id = qs.get("v", [None])[0]
                if video_id:
                    return f"https://www.youtube.com/embed/{video_id}"

            # Playlist: https://www.youtube.com/playlist?list=PLAYLIST_ID
            if parsed.path == "/playlist":
                qs = parse_qs(parsed.query)
                playlist_id = qs.get("list", [None])[0]
                if playlist_id:
                    return f"https://www.youtube.com/embed/videoseries?list={playlist_id}"

        # Vídeo curt: https://youtu.be/VIDEO_ID
        if "youtu.be" in netloc:
            video_id = parsed.path.lstrip("/")
            if video_id:
                return f"https://www.youtube.com/embed/{video_id}"

        # ---------- TWITCH ----------
        # Exemple: https://www.twitch.tv/CANAL
        if "twitch.tv" in netloc:
            channel = parsed.path.lstrip("/")
            if channel:
                # IMPORTANT: canvia 'localhost' pel teu domini real en producció
                return f"https://player.twitch.tv/?channel={channel}&parent=localhost"

        # Fallback: retornem la URL tal qual
        return url

    # --- Gestió d'imatges (PART 8.2) ---

    def _resize_and_optimize_thumbnail(self):
        """
        Redimensiona i optimitza la imatge de thumbnail per ús web.
        """
        if not self.thumbnail:
            return

        try:
            img = Image.open(self.thumbnail)
        except Exception:
            return

        img = img.convert("RGB")
        max_size = (1280, 720)
        img.thumbnail(max_size, Image.LANCZOS)

        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=80, optimize=True)
        buffer.seek(0)

        filename = os.path.basename(self.thumbnail.name)
        self.thumbnail.save(filename, ContentFile(buffer.read()), save=False)

    def get_default_thumbnail_url(self) -> str:
        """
        Retorna una imatge per defecte en funció de la categoria.
        No toca la base de dades, només retorna una URL a /static/.
        """
        mapping = {
            "Gaming": "ivents/img/default_gaming.jpg",
            "Música": "ivents/img/default_music.jpg",
            "Xerrades": "ivents/img/default_talk.jpg",
            "Educació": "ivents/img/default_education.jpg",
            "Esports": "ivents/img/default_sports.jpg",
            "Entreteniment": "ivents/img/default_entertainment.jpg",
            "Tecnologia": "ivents/img/default_technology.jpg",
            "Art i Creativitat": "ivents/img/default_art.jpg",
            "Altres": "ivents/img/default_other.jpg",
        }
        path = mapping.get(self.category, "ivents/img/default_other.jpg")
        return static(path)

    def get_thumbnail_url(self) -> str:
        """
        Retorna una URL per <img>:

        - Si hi ha una URL absoluta guardada al camp -> la retorna.
        - Si hi ha un fitxer pujat -> .url
        - Si no hi ha res -> imatge per defecte per categoria.
        """
        if self.thumbnail:
            name = str(self.thumbnail)

            # Cas 1: URL absoluta
            if name.startswith("http://") or name.startswith("https://"):
                return name

            # Cas 2: fitxer pujat
            try:
                return self.thumbnail.url
            except ValueError:
                return name

        # Fallback: imatge per defecte
        return self.get_default_thumbnail_url()

    def save(self, *args, **kwargs):
        """
        Sobreescrivim save per optimitzar la imatge de thumbnail.
        """
        # Guardem primer
        super().save(*args, **kwargs)

        # Si hi ha thumbnail, la redimensionem i tornem a guardar
        if self.thumbnail:
            self._resize_and_optimize_thumbnail()
            super().save(update_fields=["thumbnail", "updated_at"])

    # --- Sistema d'estats automàtic  ---

    @classmethod
    def auto_update_statuses(cls):
        """
        Actualitza automàticament els estats:
        - scheduled -> live quan s'arriba a l'hora programada
        - live -> finished quan s'ha superat la durada estimada
        Retorna un diccionari amb estadístiques de canvis.
        """
        now = timezone.now()
        stats = {"scheduled_to_live": 0, "live_to_finished": 0}

        # scheduled -> live
        scheduled_qs = cls.objects.filter(
            status="scheduled",
            scheduled_date__lte=now,
        )
        for ev in scheduled_qs:
            ev.status = "live"
            ev.save(update_fields=["status", "updated_at"])
            stats["scheduled_to_live"] += 1

        # live -> finished (en funció de la durada estimada)
        live_qs = cls.objects.filter(
            status="live",
            scheduled_date__isnull=False,
        )
        for ev in live_qs:
            minutes = CATEGORY_ESTIMATED_DURATION.get(ev.category, 90)
            end_time = ev.scheduled_date + timedelta(minutes=minutes)
            if end_time <= now:
                ev.status = "finished"
                ev.save(update_fields=["status", "updated_at"])
                stats["live_to_finished"] += 1

        return stats

    # --- Sistema d'etiquetes  ---

    @classmethod
    def get_tag_cloud(cls, limit: int = 50):
        """
        Retorna una llista [(tag, count), ...] ordenada per ús descendent.
        """
        counter = Counter()
        for ev in cls.objects.all():
            for tag in ev.get_tags_list():
                counter[tag] += 1
        return counter.most_common(limit)

    @classmethod
    def search_tags(cls, query: str, limit: int = 10) -> list[str]:
        """
        Retorna una llista d'etiquetes que comencen pel prefix donat (case-insensitive),
        ordenades per popularitat.
        """
        if not query:
            return []

        q = query.strip().lower()
        counter = Counter()

        for ev in cls.objects.all():
            for tag in ev.get_tags_list():
                if tag.lower().startswith(q):
                    counter[tag] += 1

        return [t for t, _ in counter.most_common(limit)]
