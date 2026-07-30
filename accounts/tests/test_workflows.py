from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class InscriptionConnexionWorkflowTest(TestCase):
    def test_inscription_cree_un_compte_et_connecte_l_utilisateur(self):
        response = self.client.post(
            reverse("accounts:inscription"),
            {
                "username": "charlie",
                "email": "charlie@example.com",
                "password1": "MotDePasseSolide123",
                "password2": "MotDePasseSolide123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="charlie").exists())

    def test_connexion_avec_identifiants_valides(self):
        User.objects.create_user("dora", password="MotDePasseSolide123")
        response = self.client.post(
            reverse("accounts:connexion"),
            {"username": "dora", "password": "MotDePasseSolide123"},
        )
        self.assertEqual(response.status_code, 302)

    def test_connexion_avec_mauvais_mot_de_passe_echoue(self):
        User.objects.create_user("dora", password="MotDePasseSolide123")
        response = self.client.post(
            reverse("accounts:connexion"),
            {"username": "dora", "password": "mauvais"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_deconnexion(self):
        User.objects.create_user("dora", password="MotDePasseSolide123")
        self.client.login(username="dora", password="MotDePasseSolide123")
        response = self.client.post(reverse("accounts:deconnexion"))
        self.assertEqual(response.status_code, 302)
