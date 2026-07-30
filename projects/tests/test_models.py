from django.contrib.auth.models import User
from django.test import TestCase

from projects.models import Projet, Tache


class ProjetModelTest(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user("alice", password="pass12345")
        self.bob = User.objects.create_user("bob", password="pass12345")

    def test_creation_projet(self):
        projet = Projet.objects.create(nom="Site web", createur=self.alice)
        self.assertEqual(str(projet), "Site web")
        self.assertEqual(projet.createur, self.alice)

    def test_relation_membres_many_to_many(self):
        projet = Projet.objects.create(nom="App mobile", createur=self.alice)
        projet.membres.add(self.bob)
        self.assertIn(self.bob, projet.membres.all())

    def test_nb_taches(self):
        projet = Projet.objects.create(nom="API", createur=self.alice)
        Tache.objects.create(titre="Concevoir le schéma", projet=projet)
        Tache.objects.create(titre="Écrire les tests", projet=projet, statut="terminee")
        self.assertEqual(projet.nb_taches(), 2)
        self.assertEqual(projet.nb_taches_terminees(), 1)

    def test_est_accessible_par_createur(self):
        projet = Projet.objects.create(nom="Refonte", createur=self.alice)
        self.assertTrue(projet.est_accessible_par(self.alice))

    def test_est_accessible_par_membre(self):
        projet = Projet.objects.create(nom="Refonte", createur=self.alice)
        projet.membres.add(self.bob)
        self.assertTrue(projet.est_accessible_par(self.bob))

    def test_non_accessible_par_etranger(self):
        projet = Projet.objects.create(nom="Refonte", createur=self.alice)
        self.assertFalse(projet.est_accessible_par(self.bob))


class TacheModelTest(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user("alice", password="pass12345")
        self.bob = User.objects.create_user("bob", password="pass12345")
        self.projet = Projet.objects.create(nom="Refonte", createur=self.alice)

    def test_valeurs_par_defaut(self):
        tache = Tache.objects.create(titre="Rédiger le cahier des charges", projet=self.projet)
        self.assertEqual(tache.statut, "a_faire")
        self.assertEqual(tache.priorite, "moyenne")
        self.assertIsNone(tache.assigne)

    def test_assignation_tache(self):
        self.projet.membres.add(self.bob)
        tache = Tache.objects.create(
            titre="Corriger le bug de connexion",
            projet=self.projet,
            assigne=self.bob,
            statut="en_cours",
            priorite="haute",
        )
        self.assertEqual(tache.assigne, self.bob)
        self.assertEqual(tache.get_statut_display(), "En cours")

    def test_suppression_projet_supprime_les_taches(self):
        Tache.objects.create(titre="Tâche 1", projet=self.projet)
        Tache.objects.create(titre="Tâche 2", projet=self.projet)
        self.projet.delete()
        self.assertEqual(Tache.objects.count(), 0)

    def test_assigner_une_tache_ajoute_automatiquement_le_membre(self):
        """
        Correctif du bug : assigner une tâche à quelqu'un qui n'est pas encore
        membre du projet doit l'ajouter automatiquement aux membres, pour
        qu'il puisse ensuite modifier le statut de sa tâche.
        """
        self.assertFalse(self.projet.membres.filter(pk=self.bob.pk).exists())
        Tache.objects.create(titre="Nouvelle tâche pour Bob", projet=self.projet, assigne=self.bob)
        self.assertTrue(self.projet.membres.filter(pk=self.bob.pk).exists())

    def test_assigner_au_createur_ne_l_ajoute_pas_deux_fois_aux_membres(self):
        Tache.objects.create(titre="Tâche pour Alice", projet=self.projet, assigne=self.alice)
        self.assertFalse(self.projet.membres.filter(pk=self.alice.pk).exists())
