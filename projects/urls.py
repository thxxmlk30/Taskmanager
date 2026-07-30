from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path("", views.liste_projets, name="liste_projets"),
    path("nouveau/", views.creer_projet, name="creer_projet"),
    path("<int:pk>/", views.projet_detail, name="projet_detail"),
    path("<int:pk>/modifier/", views.modifier_projet, name="modifier_projet"),
    path("<int:pk>/supprimer/", views.supprimer_projet, name="supprimer_projet"),
    path("<int:projet_pk>/taches/nouvelle/", views.creer_tache, name="creer_tache"),
    path("<int:projet_pk>/taches/<int:pk>/modifier/", views.modifier_tache, name="modifier_tache"),
    path("<int:projet_pk>/taches/<int:pk>/statut/", views.changer_statut_tache, name="changer_statut_tache"),
    path("<int:projet_pk>/taches/<int:pk>/supprimer/", views.supprimer_tache, name="supprimer_tache"),
]
