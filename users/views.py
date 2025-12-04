from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db import DatabaseError

from .forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm,
    CustomUserUpdateForm
)

User = get_user_model()


# 2.1 REGISTRE
def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, "Compte creat correctament! 🎉")
                return redirect("home")
            except DatabaseError:
                messages.error(request, "Error inesperat. Torna-ho a provar.")
        return render(request, "registration/register.html", {"form": form})
    else:
        form = CustomUserCreationForm()

    return render(request, "registration/register.html", {"form": form})


# 2.2 LOGIN
def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Benvingut/da, {user.display_name or user.username} 👋")
            return redirect("home")
        else:
            messages.error(request, "Usuari o contrasenya incorrectes.")
    else:
        form = CustomAuthenticationForm()

    return render(request, "registration/login.html", {"form": form})


# 2.3 LOGOUT
def logout_view(request):
    logout(request)
    messages.info(request, "Sessió tancada correctament.")
    return redirect("home")


# HOME
def home_view(request):
    return render(request, "home.html")


# 2.4 PERFIL PROPI
@login_required
def profile_view(request):
    return render(request, "users/profile.html")


# 2.5 EDITAR PERFIL
@login_required
def edit_profile_view(request):
    if request.method == "POST":
        form = CustomUserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualitzat correctament ")
            return redirect("users:profile")
    else:
        form = CustomUserUpdateForm(instance=request.user)

    return render(request, "users/edit_profile.html", {"form": form})


# 2.6 PERFIL PÚBLIC
def public_profile_view(request, username):
    user_profile = get_object_or_404(User, username=username)
    return render(request, "users/public_profile.html", {"user_profile": user_profile})
