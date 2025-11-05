from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

User = get_user_model()


# 1.1 Formulari de Registre
class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Contrasenya",
        widget=forms.PasswordInput,
        help_text="La contrasenya ha de ser segura i coincideixi amb la confirmació."
    )
    password2 = forms.CharField(
        label="Repeteix la contrasenya",
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]

    # Validació email únic
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Aquest email ja està registrat.")
        return email

    # Validació coincidir contrasenyes i complexitat
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Les contrasenyes no coincideixen.")

        validate_password(password1)  # Aplica els validadors de Django
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user



# 1.2 Formulari d'Edició de Perfil
class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "display_name", "bio", "avatar"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "avatar": forms.FileInput(attrs={"class": "form-control"}),
        }



# 1.3 Formulari d'Autenticació (Login amb email o username)
class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuari o Email",
        widget=forms.TextInput(attrs={"autofocus": True})
    )

    def clean(self):
        username_or_email = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        try:
            # Si el que escriu és un email → buscar usuari
            if "@" in username_or_email:
                user = User.objects.get(email=username_or_email)
                self.cleaned_data["username"] = user.username
        except User.DoesNotExist:
            pass  # Es provarà l'autenticació normal

        return super().clean()
