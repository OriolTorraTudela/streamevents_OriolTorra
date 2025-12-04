from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

from .views import (
    register_view, login_view, logout_view,
    profile_view, edit_profile_view, public_profile_view
)

app_name = "users"

urlpatterns = [
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile_view, name="profile"),
    path("profile/edit/", edit_profile_view, name="edit_profile"),

    # CANVIAR CONTRASENYA (usuari ja autenticat)
    path(
        "password-change/",
        auth_views.PasswordChangeView.as_view(
            template_name="registration/password_reset.html",
            success_url=reverse_lazy("users:password_change_done")
        ),
        name="password_change",
    ),

    path(
        "password-change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="registration/password_reset.html"
        ),
        name="password_change_done",
    ),

    # PERFIL PÚBLIC (última perquè no tapi rutes)
    path("<str:username>/", public_profile_view, name="public_profile"),
]
