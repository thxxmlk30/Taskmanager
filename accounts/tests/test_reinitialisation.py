import re

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse


class MotDePasseOublieTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            "eve", email="eve@example.com", password="AncienMotDePasse123"
        )

    def test_page_de_demande_accessible(self):
        response = self.client.get(reverse("accounts:mot_de_passe_oublie"))
        self.assertEqual(response.status_code, 200)

    def test_demande_avec_email_existant_envoie_un_mail(self):
        response = self.client.post(
            reverse("accounts:mot_de_passe_oublie"), {"email": "eve@example.com"}
        )
        self.assertRedirects(response, reverse("accounts:mot_de_passe_oublie_envoye"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("eve@example.com", mail.outbox[0].to)

    def test_demande_avec_email_inconnu_ne_revele_pas_l_absence_de_compte(self):
        """Par sécurité, on affiche le même message que l'email existe ou non :
        cela évite qu'un attaquant devine quels e-mails sont enregistrés."""
        response = self.client.post(
            reverse("accounts:mot_de_passe_oublie"), {"email": "inconnu@example.com"}
        )
        self.assertRedirects(response, reverse("accounts:mot_de_passe_oublie_envoye"))
        self.assertEqual(len(mail.outbox), 0)

    def test_parcours_complet_de_reinitialisation(self):
        # 1. Demande de réinitialisation
        self.client.post(reverse("accounts:mot_de_passe_oublie"), {"email": "eve@example.com"})
        self.assertEqual(len(mail.outbox), 1)

        # 2. Extraction du lien réel envoyé par e-mail
        corps = mail.outbox[0].body
        match = re.search(r"/mot-de-passe-oublie/confirmer/(?P<uidb64>[\w-]+)/(?P<token>[\w-]+)/", corps)
        self.assertIsNotNone(match, "Le lien de réinitialisation n'a pas été trouvé dans l'e-mail.")

        # 3. Premier accès au lien : Django redirige vers une URL "set-password"
        #    et place le vrai token en session (comportement standard de Django).
        lien = f"/accounts{match.group(0)}"
        reponse_lien = self.client.get(lien, follow=True)
        self.assertEqual(reponse_lien.status_code, 200)

        # 4. Soumission du nouveau mot de passe
        url_confirmee = reponse_lien.redirect_chain[-1][0]
        reponse_post = self.client.post(
            url_confirmee,
            {"new_password1": "NouveauMotDePasse456", "new_password2": "NouveauMotDePasse456"},
        )
        self.assertRedirects(reponse_post, reverse("accounts:mot_de_passe_termine"))

        # 5. Le nouveau mot de passe fonctionne bien pour se connecter
        self.user.refresh_from_db()
        connexion = self.client.post(
            reverse("accounts:connexion"),
            {"username": "eve", "password": "NouveauMotDePasse456"},
        )
        self.assertEqual(connexion.status_code, 302)

    def test_lien_invalide_affiche_un_message_clair(self):
        response = self.client.get(
            reverse(
                "accounts:mot_de_passe_confirmer",
                kwargs={"uidb64": "invalide", "token": "invalide"},
            ),
            follow=True,
        )
        self.assertContains(response, "invalide")
