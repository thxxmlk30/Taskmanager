"""
Configuration des URLs du projet.
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("projects/", include("projects.urls")),
    path("", RedirectView.as_view(pattern_name="projects:liste_projets"), name="accueil"),
]
