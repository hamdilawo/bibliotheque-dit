# FROM est toujours la première instruction d'un Dockerfile 
# From est le point de départ de ton image.
# From définit image de base 
# slim est la version legère 
FROM python:3.14-slim
# Création du groupe système et utilisateur système
# Sans cette commande — l'app tourne en tant que ROOT
# Avec cette commande — l'app tourne en tant que appuser
RUN groupadd -r appuser && useradd -r -g appuser appuser
# WORKDIR définit le répertoire de travail dans le conteneur 
# c'est le dossier dans lequel toutes les commandes  seront 
# exécutées.
# Sans WORKDIR — tout s'exécute à la racine /
# Crée /app et se place dedans , équivant de mkdir
WORKDIR /app
# --no-install-recommends :  installe uniquement le strict 
# nécessaire (image plus légère)
# libpq-dev: bibliothèque PostgreSQL — nécessaire pour psycopg2
# gcc:  compilateur C — nécessaire pour compiler psycopg2
# rm -rf /var/lib/apt/lists/* :
# Supprime le cache apt après installation
# Alternative plus légère: psycopg2-binary
# Si on utilise psycopg2-binary dans requirements.txt
# On n'a pas besoin de libpq-dev et gcc
# psycopg2 : besoin de libpq-dev et gcc
#RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# COPY copie des fichiers depuis ta machine locale 
# vers le conteneur Docker.
# copie requirements.txt dans /app/requirements.txt
# . = répertoire courant dans le conteneur
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

EXPOSE 8002
CMD ["python", "manage.py", "runserver", "0.0.0.0:8002"]
