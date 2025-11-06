from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

User = get_user_model()


# 1.1 Formulari de Registre
class CustomUserCreationForm(forms.ModelForm):
    username = forms.CharField(
        label="Nom d'usuari",
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9.@+\-_]+$',
                message="El nom d'usuari només pot contenir lletres, números i els caràcters @ . + - _",
            )
        ],
        widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"})
    )

    password1 = forms.CharField(
        label="Contrasenya",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        help_text="La contrasenya ha de ser segura i coincideixi amb la confirmació."
    )

    password2 = forms.CharField(
        label="Repeteix la contrasenya",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
        }

    #  Validació email segura amb Djongo
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            return email
        try:
            User.objects.get(email=email)
            raise ValidationError("Aquest email ja està registrat.")
        except User.DoesNotExist:
            return email

    #  Validació passwords
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Les contrasenyes no coincideixen.")
            return cleaned_data

        try:
            validate_password(password1)
        except ValidationError as e:
            self.add_error("password1", e)

        return cleaned_data

    #  Guardat segur
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
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "display_name": forms.TextInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "avatar": forms.FileInput(attrs={"class": "form-control"}),
        }



# 1.3 Formulari d'Autenticació (Login amb email o username)
class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuari o Email",
        widget=forms.TextInput(attrs={"autofocus": True, "class": "form-control"})
    )
    password = forms.CharField(
        label="Contrasenya",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    def clean(self):
        username_or_email = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        # Si sembla email → busquem usuari
        if "@" in username_or_email:
            try:
                user = User.objects.get(email=username_or_email)
                self.cleaned_data["username"] = user.username
            except User.DoesNotExist:
                pass

        return super().clean()
