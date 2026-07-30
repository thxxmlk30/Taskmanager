from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from projects.models import Projet, Tache


class ProjetViewsTest(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user("alice", password="pass12345")
        self.bob = User.objects.create_user("bob", password="pass12345")
        self.projet = Projet.objects.create(nom="Projet Alice", createur=self.alice)

    def test_liste_projets_redirige_si_non_connecte(self):
        response = self.client.get(reverse("projects:liste_projets"))
        self.assertEqual(response.status_code, 302)

    def test_liste_projets_affiche_seulement_les_projets_de_l_utilisateur(self):
        self.client.login(username="bob", password="pass12345")
        response = self.client.get(reverse("projects:liste_projets"))
        self.assertNotContains(response, "Projet Alice")

    def test_createur_voit_son_projet(self):
        self.client.login(username="alice", password="pass12345")
        response = self.client.get(reverse("projects:liste_projets"))
        self.assertContains(response, "Projet Alice")

    def test_creation_projet_via_formulaire(self):
        self.client.login(username="alice", password="pass12345")
        response = self.client.post(
            reverse("projects:creer_projet"), {"nom": "Nouveau projet", "description": "Test"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Projet.objects.filter(nom="Nouveau projet").exists())

    def test_non_membre_ne_peut_pas_voir_le_detail(self):
        self.client.login(username="bob", password="pass12345")
        response = self.client.get(reverse("projects:projet_detail", args=[self.projet.pk]))
        self.assertEqual(response.status_code, 403)

    def test_membre_peut_voir_le_detail(self):
        self.projet.membres.add(self.bob)
        self.client.login(username="bob", password="pass12345")
        response = self.client.get(reverse("projects:projet_detail", args=[self.projet.pk]))
        self.assertEqual(response.status_code, 200)

    def test_seul_le_createur_peut_supprimer_le_projet(self):
        self.projet.membres.add(self.bob)
        self.client.login(username="bob", password="pass12345")
        response = self.client.get(reverse("projects:supprimer_projet", args=[self.projet.pk]))
        self.assertEqual(response.status_code, 403)


class TacheViewsTest(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user("alice", password="pass12345")
        self.bob = User.objects.create_user("bob", password="pass12345")
        self.projet = Projet.objects.create(nom="Projet", createur=self.alice)

    def test_creation_tache(self):
        self.client.login(username="alice", password="pass12345")
        response = self.client.post(
            reverse("projects:creer_tache", args=[self.projet.pk]),
            {"titre": "Ma tâche", "statut": "a_faire", "priorite": "moyenne"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Tache.objects.filter(titre="Ma tâche").exists())

    def test_suppression_tache(self):
        self.client.login(username="alice", password="pass12345")
        tache = Tache.objects.create(titre="À supprimer", projet=self.projet)
        response = self.client.post(
            reverse("projects:supprimer_tache", args=[self.projet.pk, tache.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Tache.objects.filter(pk=tache.pk).exists())

    # --- Scénario du bug signalé : l'assigné doit pouvoir changer le statut ---

    def test_assigner_puis_l_assigne_peut_modifier_le_statut(self):
        """
        Reproduction exacte du bug rapporté : Alice crée une tâche et
        l'assigne à Bob, qui n'était pas membre du projet auparavant.
        Bob doit pouvoir ouvrir le formulaire et passer la tâche à "Terminée".
        """
        self.client.login(username="alice", password="pass12345")
        creation = self.client.post(
            reverse("projects:creer_tache", args=[self.projet.pk]),
            {"titre": "Tâche pour Bob", "assigne": self.bob.id, "statut": "a_faire", "priorite": "moyenne"},
        )
        self.assertEqual(creation.status_code, 302)
        tache = Tache.objects.get(titre="Tâche pour Bob")

        # Bob n'a jamais été ajouté manuellement comme membre.
        self.client.logout()
        self.client.login(username="bob", password="pass12345")

        # Il doit pouvoir accéder au formulaire de modification...
        acces = self.client.get(
            reverse("projects:modifier_tache", args=[self.projet.pk, tache.pk])
        )
        self.assertEqual(acces.status_code, 200)

        # ...et changer le statut avec succès.
        modification = self.client.post(
            reverse("projects:modifier_tache", args=[self.projet.pk, tache.pk]),
            {"titre": "Tâche pour Bob", "assigne": self.bob.id, "statut": "terminee", "priorite": "moyenne"},
        )
        self.assertEqual(modification.status_code, 302)
        tache.refresh_from_db()
        self.assertEqual(tache.statut, "terminee")

    def test_assigne_devient_visible_dans_la_liste_de_ses_projets(self):
        self.client.login(username="alice", password="pass12345")
        self.client.post(
            reverse("projects:creer_tache", args=[self.projet.pk]),
            {"titre": "Tâche pour Bob", "assigne": self.bob.id, "statut": "a_faire", "priorite": "moyenne"},
        )
        self.client.logout()
        self.client.login(username="bob", password="pass12345")
        response = self.client.get(reverse("projects:liste_projets"))
        self.assertContains(response, "Projet")

    def test_etranger_au_projet_ne_peut_pas_modifier_une_tache(self):
        tache = Tache.objects.create(titre="Tâche neutre", projet=self.projet)
        self.client.login(username="bob", password="pass12345")
        response = self.client.get(
            reverse("projects:modifier_tache", args=[self.projet.pk, tache.pk])
        )
        self.assertEqual(response.status_code, 403)


class ChangerStatutTacheViewTest(TestCase):
    """Le tableau des tâches permet de changer le statut directement,
    sans passer par la page complète 'Modifier'."""

    def setUp(self):
        self.alice = User.objects.create_user("alice", password="pass12345")
        self.bob = User.objects.create_user("bob", password="pass12345")
        self.projet = Projet.objects.create(nom="Projet", createur=self.alice)
        self.tache = Tache.objects.create(titre="Tâche", projet=self.projet, assigne=self.bob)

    def test_get_non_autorise(self):
        """La mise à jour ne doit se faire qu'en POST (require_POST)."""
        self.client.login(username="alice", password="pass12345")
        response = self.client.get(
            reverse("projects:changer_statut_tache", args=[self.projet.pk, self.tache.pk])
        )
        self.assertEqual(response.status_code, 405)

    def test_le_createur_peut_changer_le_statut(self):
        self.client.login(username="alice", password="pass12345")
        response = self.client.post(
            reverse("projects:changer_statut_tache", args=[self.projet.pk, self.tache.pk]),
            {"statut": "en_cours"},
        )
        self.assertRedirects(response, reverse("projects:projet_detail", args=[self.projet.pk]))
        self.tache.refresh_from_db()
        self.assertEqual(self.tache.statut, "en_cours")

    def test_l_assigne_peut_changer_le_statut_sans_passer_par_modifier(self):
        self.client.login(username="bob", password="pass12345")
        response = self.client.post(
            reverse("projects:changer_statut_tache", args=[self.projet.pk, self.tache.pk]),
            {"statut": "terminee"},
        )
        self.assertRedirects(response, reverse("projects:projet_detail", args=[self.projet.pk]))
        self.tache.refresh_from_db()
        self.assertEqual(self.tache.statut, "terminee")

    def test_statut_invalide_est_rejete(self):
        self.client.login(username="alice", password="pass12345")
        self.client.post(
            reverse("projects:changer_statut_tache", args=[self.projet.pk, self.tache.pk]),
            {"statut": "valeur-inventee"},
        )
        self.tache.refresh_from_db()
        self.assertEqual(self.tache.statut, "a_faire")

    def test_etranger_ne_peut_pas_changer_le_statut(self):
        User.objects.create_user("etranger", password="pass12345")
        self.client.login(username="etranger", password="pass12345")
        response = self.client.post(
            reverse("projects:changer_statut_tache", args=[self.projet.pk, self.tache.pk]),
            {"statut": "terminee"},
        )
        self.assertEqual(response.status_code, 403)
        self.tache.refresh_from_db()
        self.assertEqual(self.tache.statut, "a_faire")

    def test_le_select_de_statut_apparait_dans_la_page_projet(self):
        self.client.login(username="alice", password="pass12345")
        response = self.client.get(reverse("projects:projet_detail", args=[self.projet.pk]))
        self.assertContains(response, "statut-select")
