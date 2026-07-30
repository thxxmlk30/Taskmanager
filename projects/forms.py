from django import forms
from django.contrib.auth import get_user_model

from .models import Projet, Tache

User = get_user_model()


class ProjetForm(forms.ModelForm):
    class Meta:
        model = Projet
        fields = ["nom", "description", "membres"]
        widgets = {
            "nom": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "membres": forms.SelectMultiple(attrs={"class": "form-select"}),
        }


class TacheForm(forms.ModelForm):
    class Meta:
        model = Tache
        fields = ["titre", "description", "assigne", "statut", "priorite", "date_echeance"]
        widgets = {
            "titre": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "assigne": forms.Select(attrs={"class": "form-select"}),
            "statut": forms.Select(attrs={"class": "form-select"}),
            "priorite": forms.Select(attrs={"class": "form-select"}),
            "date_echeance": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

    def __init__(self, *args, projet=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._projet = projet
        if projet is not None:
            # Le champ "assigne" propose le créateur, les membres déjà présents,
            # ET tous les autres utilisateurs (on peut assigner quelqu'un de
            # nouveau : il deviendra automatiquement membre à l'enregistrement,
            # voir Tache.save()).
            self.fields["assigne"].queryset = User.objects.all().order_by("username")
