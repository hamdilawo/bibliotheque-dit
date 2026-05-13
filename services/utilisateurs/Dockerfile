# Dans Docker, l'environnement virtuel est inutile 
# car chaque conteneur est déjà isolé.

# FROM est toujours la première instruction d'un Dockerfile 
# From est le point de départ de ton image.
# From définit image de base 
# FROM python:3.14 ne fait pas qu'importer Python 
# il importe une image complète qui contient déjà 
# tout un système Linux + Python. 
# FROM python:3.14 contient: Linux (Debian/Ubuntu),
# Python 3.14,pip, outils de base(bash,curl )
# slim est la version legère 
# Les différentes variantes de l'image Python:
#FROM python:3.14 :  image complète — plus lourde (~900MB)
#FROM python:3.14-slim :   image légère — recommandée (~150MB)
#FROM python:3.14-alpine : image très légère — (~50MB)

FROM python:3.14-slim
# groupadd -r appuser: crée un groupe système , -r=system group
# useradd -r -g appuser appuser(nom de l'utilisateur = appuser) : 
# crée un utilisateur
# -r = utilisateur système (system user)
# -g appuser = appartient au groupe appuser
# Sans cette commande — l'app tourne en tant que ROOT
# Dangereux ! Si quelqu'un pirate l'app → 
# accès ROOT au conteneur
# Avec cette commande — l'app tourne en tant que appuser
RUN groupadd -r appuser && useradd -r -g appuser appuser
# WORKDIR définit le répertoire de travail dans le conteneur 
# c'est le dossier dans lequel toutes les commandes  seront 
# exécutées.
# Sans WORKDIR — tout s'exécute à la racine /
# Crée /app et se place dedans , équivant de mkdir
WORKDIR /app
# apt-get update: Met à jour la liste des paquets disponibles
# Obligatoire avant toute installation
# apt-get install : installe des paquets
# -y :  répond "oui" automatiquement à toutes les questions
# --no-install-recommends :  installe uniquement le strict 
# nécessaire (image plus légère)
# libpq-dev: bibliothèque PostgreSQL — nécessaire pour psycopg2
# gcc:  compilateur C — nécessaire pour compiler psycopg2
# rm -rf /var/lib/apt/lists/* :
# Supprime le cache apt après installation
# Réduit la taille de l'image Docke
# Pourquoi tout en une seule commande RUN ?
# Bon — un seul layer → image plus légère
# Et ne crée non pas 3 layers Docker séparés → image plus lourde
# Alternative plus légère: psycopg2-binary
# Si on utilise psycopg2-binary dans requirements.txt
# On n'a pas besoin de libpq-dev et gcc
# psycopg2 : besoin de libpq-dev et gcc
#RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# COPY copie des fichiers depuis ta machine locale 
# vers le conteneur Docker.
# copie requirements.txt dans /app/requirements.txt
# . = répertoire courant dans le conteneur
# Pourquoi copier requirements.txt avant le reste ?
# Bonne pratique — copier requirements.txt EN PREMIER
# Raison → optimisation du cache Docker :
# Si ton code change mais pas requirements.txt
# Docker réutilise le layer pip install  plus rapide
COPY requirements.txt .
# --no-cache-dir :dit à pip de ne pas sauvegarder de cache 
# lors de l'installation des packages.
# pas de cache sauvegardé → image plus légère
RUN pip install --no-cache-dir -r requirements.txt

# Copie tout le contenu du répertoire courant de ta 
# machine locale vers le répertoire de travail du conteneur.
# premier '.': source = répertoire courant de ta machine (.)
# deuxième '.': destination = WORKDIR du conteneur (/app)
COPY . .
# chown = change owner: change le propriétaire 
# d'un fichier ou dossier.
# -R = Recursif (tous les sous-dossiers)
appuser:appuser -> group:user
RUN chown -R appuser:appuser /app
# USER définit quel utilisateur exécute les commandes 
# suivantes dans le conteneur.
# il s'agit  de utilisateur nommé appuser
# USER doit être placé après toutes les commandes qui 
# nécessitent les droits ROOT (apt-get, pip install, chown...) 
# et avant CMD.
USER appuser

# EXPOSE documente le port sur lequel l'application écoute 
# dans le conteneur.
# Indique que le conteneur écoute sur le port 8002
#  Important: EXPOSE ne publie pas le port
# EXPOSE = documentation uniquement
# Il n'ouvre PAS réellement le port

# C'est docker-compose qui publie vraiment le port
# à travers la ligne suivante dans le docker-compose.yml
#ports:
#    - "8002:8002"  # machine_locale:conteneur
# ANALOGIE
# EXPOSE  → indique quelle porte existe dans la maison
# ports   → ouvre vraiment la porte vers l'extérieur
# Aucun problème ! En local et dans Docker ce sont deux 
# environnements complètement séparés.
# http://localhost:8000 et http://localhost:8002 peuvent
# tourner en même temps sans conflit 
EXPOSE 8002
CMD ["python", "manage.py", "runserver", "0.0.0.0:8002"]
