from django.contrib import admin

from .models import Projet, Tache


@admin.register(Projet)
class ProjetAdmin(admin.ModelAdmin):
    list_display = ("nom", "createur", "date_creation")
    search_fields = ("nom",)


@admin.register(Tache)
class TacheAdmin(admin.ModelAdmin):
    list_display = ("titre", "projet", "assigne", "statut", "priorite", "date_echeance")
    list_filter = ("statut", "priorite")
    search_fields = ("titre",)
