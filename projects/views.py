from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProjetForm, TacheForm
from .models import Projet, Tache


def _peut_voir_le_projet(projet, user):
    return projet.est_accessible_par(user)


def _peut_gerer_la_tache(tache, user):
    """
    Autorise l'accès à une tâche si l'utilisateur est créateur ou membre du
    projet, OU s'il est la personne assignée à cette tâche précise. Ce dernier
    cas est une sécurité supplémentaire : même si, pour une raison quelconque,
    l'assigné n'a pas (encore) été ajouté aux membres du projet, il doit
    toujours pouvoir mettre à jour le statut de SA PROPRE tâche.
    """
    return tache.projet.est_accessible_par(user) or tache.assigne_id == user.id


@login_required
def liste_projets(request):
    projets = Projet.objects.filter(
        Q(createur=request.user) | Q(membres=request.user)
    ).distinct()
    return render(request, "projects/liste_projets.html", {"projets": projets})


@login_required
def creer_projet(request):
    if request.method == "POST":
        form = ProjetForm(request.POST)
        if form.is_valid():
            projet = form.save(commit=False)
            projet.createur = request.user
            projet.save()
            form.save_m2m()
            messages.success(request, "Projet créé avec succès.")
            return redirect("projects:projet_detail", pk=projet.pk)
    else:
        form = ProjetForm()
    return render(request, "projects/projet_form.html", {"form": form, "creation": True})


@login_required
def projet_detail(request, pk):
    projet = get_object_or_404(Projet, pk=pk)
    if not _peut_voir_le_projet(projet, request.user):
        return HttpResponseForbidden("Vous n'avez pas accès à ce projet.")
    taches = projet.taches.all()
    return render(
        request, "projects/projet_detail.html", {"projet": projet, "taches": taches}
    )


@login_required
def modifier_projet(request, pk):
    projet = get_object_or_404(Projet, pk=pk)
    if projet.createur_id != request.user.id:
        return HttpResponseForbidden("Seul le créateur peut modifier ce projet.")
    if request.method == "POST":
        form = ProjetForm(request.POST, instance=projet)
        if form.is_valid():
            form.save()
            messages.success(request, "Projet mis à jour.")
            return redirect("projects:projet_detail", pk=projet.pk)
    else:
        form = ProjetForm(instance=projet)
    return render(request, "projects/projet_form.html", {"form": form, "creation": False})


@login_required
def supprimer_projet(request, pk):
    projet = get_object_or_404(Projet, pk=pk)
    if projet.createur_id != request.user.id:
        return HttpResponseForbidden("Seul le créateur peut supprimer ce projet.")
    if request.method == "POST":
        projet.delete()
        messages.success(request, "Projet supprimé.")
        return redirect("projects:liste_projets")
    return render(request, "projects/projet_confirm_delete.html", {"projet": projet})


@login_required
def creer_tache(request, projet_pk):
    projet = get_object_or_404(Projet, pk=projet_pk)
    if not _peut_voir_le_projet(projet, request.user):
        return HttpResponseForbidden("Vous n'avez pas accès à ce projet.")
    if request.method == "POST":
        form = TacheForm(request.POST, projet=projet)
        if form.is_valid():
            tache = form.save(commit=False)
            tache.projet = projet
            tache.save()  # déclenche l'ajout automatique de l'assigné aux membres
            messages.success(request, "Tâche créée.")
            return redirect("projects:projet_detail", pk=projet.pk)
    else:
        form = TacheForm(projet=projet)
    return render(
        request, "projects/tache_form.html", {"form": form, "projet": projet, "creation": True}
    )


@login_required
def modifier_tache(request, projet_pk, pk):
    projet = get_object_or_404(Projet, pk=projet_pk)
    tache = get_object_or_404(Tache, pk=pk, projet=projet)
    if not _peut_gerer_la_tache(tache, request.user):
        return HttpResponseForbidden("Vous n'avez pas accès à cette tâche.")
    if request.method == "POST":
        form = TacheForm(request.POST, instance=tache, projet=projet)
        if form.is_valid():
            form.save()
            messages.success(request, "Tâche mise à jour.")
            return redirect("projects:projet_detail", pk=projet.pk)
    else:
        form = TacheForm(instance=tache, projet=projet)
    return render(
        request, "projects/tache_form.html", {"form": form, "projet": projet, "creation": False}
    )


@login_required
@require_POST
def changer_statut_tache(request, projet_pk, pk):
    """
    Mise à jour rapide du statut d'une tâche directement depuis le tableau
    de la page projet, sans passer par le formulaire complet de modification.
    """
    projet = get_object_or_404(Projet, pk=projet_pk)
    tache = get_object_or_404(Tache, pk=pk, projet=projet)
    if not _peut_gerer_la_tache(tache, request.user):
        return HttpResponseForbidden("Vous n'avez pas accès à cette tâche.")

    nouveau_statut = request.POST.get("statut")
    statuts_valides = dict(Tache.STATUT_CHOICES)
    if nouveau_statut not in statuts_valides:
        messages.error(request, "Statut invalide.")
        return redirect("projects:projet_detail", pk=projet.pk)

    tache.statut = nouveau_statut
    tache.save(update_fields=["statut"])
    messages.success(request, f"Statut de « {tache.titre} » mis à jour : {tache.get_statut_display()}.")
    return redirect("projects:projet_detail", pk=projet.pk)


@login_required
def supprimer_tache(request, projet_pk, pk):
    projet = get_object_or_404(Projet, pk=projet_pk)
    tache = get_object_or_404(Tache, pk=pk, projet=projet)
    if not _peut_gerer_la_tache(tache, request.user):
        return HttpResponseForbidden("Vous n'avez pas accès à cette tâche.")
    if request.method == "POST":
        tache.delete()
        messages.success(request, "Tâche supprimée.")
        return redirect("projects:projet_detail", pk=projet.pk)
    return render(request, "projects/tache_confirm_delete.html", {"tache": tache, "projet": projet})
