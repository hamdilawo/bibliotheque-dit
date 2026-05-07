# Service Emprunt

@Moussa
Renommer note -> comment sur l'endpoint de emprunter un livre

@Hammdy
Endpoint (pour dpoonner son avis): Rating / retour
Rule: On ne peut pas donner son avis sur un livre que l on a jamais empriunter dans le passé
on ne peut pas le faire deux fois

@moussa
Notification:
Emrunt effetué
Emprunt retourné
Retard (cron job): 3jrs avant l'echeance et l'echeance (00h00)



<!-- PROCESS -->
1 - docker compose up db
2 - uv run python manage.py migrate
3 - uv run python manage.py runserver
4 - Se rendre sur la docs: pour inserer le token (@.env.example)