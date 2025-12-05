from django import forms
from django.utils import timezone
from urllib.parse import urlparse

from events.models import Event, CATEGORY_CHOICES, STATUS_CHOICES


def _validate_stream_url_or_raise(url: str):
    """
    Valida que la URL de stream provingui de YouTube o Twitch.
    """
    if not url:
        return

    parsed = urlparse(url)
    netloc = parsed.netloc.lower()

    if (
        "youtube.com" in netloc
        or "youtu.be" in netloc
        or "twitch.tv" in netloc
    ):
        return

    raise forms.ValidationError(
        "Només s'accepten URLs de YouTube o Twitch com a streaming."
    )


class EventCreationForm(forms.ModelForm):
    """
    Formulari per crear nous esdeveniments.
    """

    scheduled_date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                "type": "datetime-local",
                "class": "form-control"
            }
        ),
        input_formats=["%Y-%m-%dT%H:%M"],
        label="Data i hora programada"
    )

    description = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
        label="Descripció"
    )

    thumbnail = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(
            attrs={"class": "form-control"}
        ),
        label="Imatge de portada"
    )

    class Meta:
        model = Event
        fields = [
            "title",
            "description",
            "category",
            "scheduled_date",
            "thumbnail",
            "max_viewers",
            "tags",
            "stream_url",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "max_viewers": forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 1000}),
            "tags": forms.TextInput(attrs={"class": "form-control", "id": "id_tags"}),
            "stream_url": forms.URLInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        # passem l'usuari des de la vista per validar títol únic per usuari
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean_scheduled_date(self):
        scheduled_date = self.cleaned_data.get("scheduled_date")
        if scheduled_date and scheduled_date < timezone.now():
            raise forms.ValidationError("La data programada no pot ser en el passat.")
        return scheduled_date

    def clean_max_viewers(self):
        max_viewers = self.cleaned_data.get("max_viewers")
        if max_viewers is None:
            return max_viewers
        if not (1 <= max_viewers <= 1000):
            raise forms.ValidationError("El màxim d'espectadors ha d'estar entre 1 i 1000.")
        return max_viewers

    def clean_stream_url(self):
        url = self.cleaned_data.get("stream_url")
        if url:
            _validate_stream_url_or_raise(url)
        return url

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")

        if self.user and title:
            exists = Event.objects.filter(
                creator=self.user,
                title__iexact=title
            ).exists()
            if exists:
                raise forms.ValidationError(
                    "Ja tens un esdeveniment amb aquest títol."
                )
        return cleaned_data


class EventUpdateForm(forms.ModelForm):
    """
    Formulari per editar esdeveniments existents.
    """

    scheduled_date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                "type": "datetime-local",
                "class": "form-control"
            }
        ),
        input_formats=["%Y-%m-%dT%H:%M"],
        label="Data i hora programada"
    )

    class Meta:
        model = Event
        fields = [
            "title",
            "description",
            "category",
            "scheduled_date",
            "thumbnail",
            "max_viewers",
            "tags",
            "status",
            "stream_url",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "max_viewers": forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 1000}),
            "tags": forms.TextInput(attrs={"class": "form-control", "id": "id_tags"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "stream_url": forms.URLInput(attrs={"class": "form-control"}),
            "thumbnail": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean_max_viewers(self):
        max_viewers = self.cleaned_data.get("max_viewers")
        if max_viewers is None:
            return max_viewers
        if not (1 <= max_viewers <= 1000):
            raise forms.ValidationError("El màxim d'espectadors ha d'estar entre 1 i 1000.")
        return max_viewers

    def clean_stream_url(self):
        url = self.cleaned_data.get("stream_url")
        if url:
            _validate_stream_url_or_raise(url)
        return url

    def clean(self):
        cleaned_data = super().clean()
        new_status = cleaned_data.get("status")
        new_date = cleaned_data.get("scheduled_date")

        # Només el creador pot canviar l'estat
        if self.instance and self.user:
            if "status" in self.changed_data and self.instance.creator != self.user:
                raise forms.ValidationError(
                    "Només el creador pot canviar l'estat de l'esdeveniment."
                )

        # No es pot canviar la data si ja està en directe
        if self.instance and self.instance.status == "En Directe":
            if "scheduled_date" in self.changed_data and new_date != self.instance.scheduled_date:
                raise forms.ValidationError(
                    "No es pot canviar la data d'un esdeveniment que ja està en directe."
                )

        return cleaned_data


class EventSearchForm(forms.Form):
    """
    Formulari de cerca i filtres per als esdeveniments.
    """

    search = forms.CharField(
        required=False,
        label="Cerca",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Cerca per títol o descripció"})
    )

    category = forms.ChoiceField(
        required=False,
        label="Categoria",
        choices=[("", "Totes les categories")] + list(CATEGORY_CHOICES),
        widget=forms.Select(attrs={"class": "form-select"})
    )

    status = forms.ChoiceField(
        required=False,
        label="Estat",
        choices=[("", "Tots els estats")] + list(STATUS_CHOICES),
        widget=forms.Select(attrs={"class": "form-select"})
    )

    tag = forms.CharField(
        required=False,
        label="Etiqueta",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Etiqueta (p. ex. valorant)"})
    )

    date_from = forms.DateField(
        required=False,
        label="Des de",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )

    date_to = forms.DateField(
        required=False,
        label="Fins a",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get("date_from")
        date_to = cleaned_data.get("date_to")

        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError(
                "La data inicial no pot ser posterior a la data final."
            )
        return cleaned_data
