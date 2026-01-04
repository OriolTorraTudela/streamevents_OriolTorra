from django import forms
from .models import ChatMessage


class ChatMessageForm(forms.ModelForm):
    # Llista bàsica (amplia-la si vols)
    FORBIDDEN_WORDS = [
        "idiota",
        "imbecil",
        "tonto",
        "gilipollas",
        "puta",
        "merda",
    ]

    class Meta:
        model = ChatMessage
        fields = ["message"]
        widgets = {
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Escriu un missatge...",
                    "maxlength": "500",
                }
            )
        }

    def clean_message(self):
        msg = self.cleaned_data.get("message", "")
        msg_stripped = msg.strip()

        if not msg_stripped:
            raise forms.ValidationError("El missatge no pot estar buit.")

        if len(msg_stripped) > 500:
            raise forms.ValidationError("El missatge no pot superar 500 caràcters.")

        lower = msg_stripped.lower()
        for w in self.FORBIDDEN_WORDS:
            if w in lower:
                raise forms.ValidationError("El missatge conté llenguatge no permès.")
        return msg_stripped
