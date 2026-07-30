# Plateforme de Gestion de Tâches

Application web Django (architecture MVT classique, templates HTML) permettant à des
équipes de créer des projets, d'assigner des tâches à leurs membres et de suivre leur
avancement.

## Stack technique

- **Backend** : Django (architecture MVT)
- **Base de données** : SQLite en local, PostgreSQL en production
- **Fichiers statiques** : Whitenoise
- **Serveur d'application** : Gunicorn
- **Tests** : unittest (Django) + pytest-django
- **CI/CD** : GitHub Actions
- **Hébergement** : Railway (PaaS)

## Démarrage rapide (local)

```bash
python -m venv venv
source venv/bin/activate        # Windows : venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Lancer les tests

```bash
pytest
```

## Fonctionnalités

- Projets avec membres, tâches avec statut/priorité/échéance/assignation
- **Mise à jour rapide du statut** directement depuis le tableau des tâches
  (menu déroulant qui s'envoie automatiquement au changement, sans passer par
  la page "Modifier")
- **Mot de passe oublié** : réinitialisation par e-mail (4 étapes standard
  Django). En local, les e-mails s'affichent dans le terminal ; voir
  `.env.example` pour configurer un vrai envoi en production.
- Pages de connexion/inscription sous forme de cartes centrées

## Correctif important — accès de l'assigné à une tâche

Quand une tâche est assignée à quelqu'un, `Tache.save()` (voir `projects/models.py`)
ajoute automatiquement cette personne aux membres du projet si elle ne l'est pas déjà.
Sans ce mécanisme, un utilisateur assigné à une tâche mais jamais ajouté manuellement
aux membres du projet se voyait refuser l'accès (erreur 403) et ne pouvait donc pas
mettre à jour le statut de sa propre tâche.

En complément, `projects/views.py` autorise explicitement l'assigné d'une tâche à la
modifier même dans le cas où, pour une raison quelconque, il n'aurait pas (encore) le
statut de membre (voir `_peut_gerer_la_tache`).

Un test de non-régression dédié reproduit ce scénario exact :
`projects/tests/test_views.py::TacheViewsTest::test_assigner_puis_l_assigne_peut_modifier_le_statut`.

## Point d'attention CI/CD

Le pipeline GitHub Actions exécute les tests avec `DEBUG=False` (pour se rapprocher des
conditions de production). Or, quand `DEBUG=False`, Django active par défaut
`SECURE_SSL_REDIRECT=True`, qui redirige (301) toute requête HTTP vers HTTPS — y compris
les requêtes du client de test, qui ne sont jamais en HTTPS. Résultat : sans précaution,
**tous les tests échouent en CI** alors qu'ils passent en local.

Le fichier `.github/workflows/ci.yml` désactive donc explicitement cette redirection
pour l'étape de test uniquement (`SECURE_SSL_REDIRECT: "False"`), et ajoute `testserver`
à `ALLOWED_HOSTS` (nom d'hôte utilisé par le client de test Django). Cela n'affaiblit en
rien la sécurité en production : sur Railway, cette variable n'est pas définie et
`SECURE_SSL_REDIRECT` reste donc à `True` par défaut.

## Point d'attention CI/CD — fichiers statiques (`collectstatic`)

Avec `DEBUG=False`, `STORAGES` utilise `CompressedManifestStaticFilesStorage`
(fichiers compressés + noms avec hash pour un cache navigateur fiable). Ce
stockage exige qu'un "manifeste" existe, généré par
`python manage.py collectstatic`. Sans cette étape, **toute page utilisant
`{% static %}` plante** avec `ValueError: Missing staticfiles manifest entry`.

Le pipeline CI et le `Procfile` (déploiement Railway) exécutent donc tous les
deux `collectstatic` avant, respectivement, les tests et `migrate`. En local,
`DEBUG=True` utilise un stockage simple : `collectstatic` n'est jamais requis
pour `runserver`.

## Déploiement

Voir le **Guide de reproduction de 0 au déploiement** fourni séparément.
