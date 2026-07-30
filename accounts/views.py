from django.contrib.auth import login
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import ConnexionForm, DemandeReinitialisationForm, InscriptionForm, NouveauMotDePasseForm


def inscription(request):
    if request.user.is_authenticated:
        return redirect("projects:liste_projets")
    if request.method == "POST":
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("projects:liste_projets")
    else:
        form = InscriptionForm()
    return render(request, "accounts/inscription.html", {"form": form})


class ConnexionView(LoginView):
    template_name = "accounts/connexion.html"
    authentication_form = ConnexionForm


class DeconnexionView(LogoutView):
    next_page = reverse_lazy("accounts:connexion")


# --- Mot de passe oublié (4 étapes standard de Django) -----------------------
#
# 1. mot_de_passe_oublie        : l'utilisateur saisit son e-mail
# 2. mot_de_passe_oublie_envoye : confirmation que l'e-mail a été envoyé (si le compte existe)
# 3. mot_de_passe_confirmer     : l'utilisateur clique le lien reçu par e-mail, choisit un nouveau mot de passe
# 4. mot_de_passe_termine       : confirmation que le mot de passe a bien été changé


class DemandeReinitialisationView(PasswordResetView):
    template_name = "accounts/mot_de_passe_oublie.html"
    email_template_name = "accounts/email/reinitialisation_corps.txt"
    subject_template_name = "accounts/email/reinitialisation_sujet.txt"
    form_class = DemandeReinitialisationForm
    success_url = reverse_lazy("accounts:mot_de_passe_oublie_envoye")


class ReinitialisationEnvoyeeView(PasswordResetDoneView):
    template_name = "accounts/mot_de_passe_oublie_envoye.html"


class ConfirmerReinitialisationView(PasswordResetConfirmView):
    template_name = "accounts/mot_de_passe_nouveau.html"
    form_class = NouveauMotDePasseForm
    success_url = reverse_lazy("accounts:mot_de_passe_termine")


class ReinitialisationTermineeView(PasswordResetCompleteView):
    template_name = "accounts/mot_de_passe_termine.html"
