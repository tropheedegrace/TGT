# Déploiement, lancement et sauvegardes UzaApp

## Démarrage local rapide

Prérequis : Python 3.12+ et le dossier du projet.

```powershell
cd "C:\Users\TROPHEE DE GRACE\Documents\APP UZA"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pytest -q
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

Ouvrir ensuite : http://localhost:8000/

La première ouverture permet de créer un compte commerce; les utilisateurs existants peuvent choisir la connexion. Les inscriptions publiques sont activées par défaut. Pour les désactiver, définir `UZAA_ALLOW_PUBLIC_REGISTRATION=false`. La route d’initialisation protégée reste disponible en définissant `UZAA_SETUP_KEY` sur le serveur.

## Vérification métier avant utilisation réelle

Avant de démarrer une utilisation réelle avec des données réelles, vérifier au minimum :

- création du compte gérant,
- création d’un compte agent,
- ajout d’une entrée avec quantité, prix d’achat et prix de vente,
- vente avec stock suffisant,
- refus d’une vente avec stock insuffisant,
- paiement d’un crédit,
- affichage du stock et des inventaires,
- déconnexion et reconnexion avec session valide.

## Essai gratuit sur Render

Le fichier `render.yaml` prépare un service web Render gratuit en HTTPS. Il peut être publié en reliant le dépôt Git à Render et en appliquant le blueprint `uzaapp-demo`. Une fois le déploiement terminé, Render fournit une URL `https://…onrender.com`; les commerçants peuvent ouvrir cette adresse et installer l’application depuis le menu du navigateur.

**Ce service gratuit est uniquement destiné aux essais avec des données fictives.** Render met le service en veille après une période d’inactivité et son système de fichiers gratuit est éphémère : SQLite peut être perdu lors d’une veille, d’un redémarrage ou d’un nouveau déploiement. Le service gratuit peut également démarrer avec un délai et est soumis à des quotas mensuels. Ne pas y inscrire de vrais commerçants ni des renseignements personnels.

Les offres gratuites des bases de données ne remplacent pas une sauvegarde : par exemple, le PostgreSQL gratuit Render a une durée limitée et n’inclut pas de sauvegardes gérées. Les conditions et tarifs des hébergeurs évoluent ; les vérifier avant toute mise en production.

## Lancement persistant avec Docker

Installe Docker Desktop, puis, dans PowerShell à la racine du projet :

```powershell
$random = [Security.Cryptography.RandomNumberGenerator]::Create()
$bytes = New-Object byte[] 32
$random.GetBytes($bytes)
$env:UZAA_RATE_LIMIT_SECRET = [Convert]::ToBase64String($bytes)
$random.Dispose()
docker compose up --build -d
```

L’application est disponible localement à `http://localhost:8000/`. Le volume Docker `uzaa_data` conserve la base au redémarrage. Pour une URL publique, déployer le conteneur derrière un hébergeur qui fournit HTTPS et un volume persistant; définir `UZAA_HTTPS_ONLY=true` et conserver `UZAA_RATE_LIMIT_SECRET` dans le gestionnaire de secrets de l’hébergeur.

## Sauvegarde SQLite

Pendant que l’application tourne, créer une sauvegarde vérifiée et conserver les 30 plus récentes :

```powershell
docker compose exec uzaapp python backup_database.py --output-dir /backups --keep 30
```

Les fichiers sont conservés dans le volume Docker `uzaa_backups`. Pour copier le dernier fichier vers le dossier courant, créer d’abord `backups`, puis utiliser `docker compose cp uzaapp:/backups/NOM_DU_FICHIER backups/`. Copier régulièrement une sauvegarde vers un emplacement indépendant et protégé (par exemple un support chiffré ou un stockage objet privé). Une sauvegarde sur le même disque que la base ne protège pas contre la perte de ce disque. Planifier cette commande quotidiennement avec le Planificateur de tâches Windows pour un déploiement Docker local; sur un hébergeur, utiliser un travail planifié et un stockage de sauvegarde externe.

Pour restaurer, arrêter l’application puis lancer `python backup_database.py --restore backups/nom-de-la-sauvegarde.sqlite3`. Le script vérifie la sauvegarde et crée une copie de la base courante avant son remplacement. Redémarrer ensuite et vérifier `/api/health` ainsi qu’une connexion avant de reprendre les opérations.

## Avant d’accueillir de vrais clients

- Utiliser une base et un disque persistants, avec sauvegardes hors site et test régulier de restauration.
- Garder secrets, sauvegardes et fichiers `.env` hors du dépôt Git.
- Activer HTTPS et `UZAA_HTTPS_ONLY=true` en production.
- Configurer la limitation de requêtes du proxy/hébergeur en plus des quotas applicatifs d’inscription.
- Surveiller les journaux, les erreurs et la consommation; établir une procédure de récupération et de réponse aux incidents.
- Tester les permissions de gérant/employé et les opérations financières sur une base de préproduction avant migration de données réelles.