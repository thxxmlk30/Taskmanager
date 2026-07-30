from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("inscription/", views.inscription, name="inscription"),
    path("connexion/", views.ConnexionView.as_view(), name="connexion"),
    path("deconnexion/", views.DeconnexionView.as_view(), name="deconnexion"),

    path(
        "mot-de-passe-oublie/",
        views.DemandeReinitialisationView.as_view(),
        name="mot_de_passe_oublie",
    ),
    path(
        "mot-de-passe-oublie/envoye/",
        views.ReinitialisationEnvoyeeView.as_view(),
        name="mot_de_passe_oublie_envoye",
    ),
    path(
        "mot-de-passe-oublie/confirmer/<uidb64>/<token>/",
        views.ConfirmerReinitialisationView.as_view(),
        name="mot_de_passe_confirmer",
    ),
    path(
        "mot-de-passe-oublie/termine/",
        views.ReinitialisationTermineeView.as_view(),
        name="mot_de_passe_termine",
    ),
]
