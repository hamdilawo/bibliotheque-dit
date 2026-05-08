# Service Emprunt

@Moussa
[x] Renommer note -> comment sur l'endpoint de emprunter un livre
[x] Sur l'Endpoint de return_loan/: retirer la prt: notes

@Hammdy [x]
Endpoint (pour dpoonner son avis): Rating / retour
Rule: On ne peut pas donner son avis sur un livre que l on a jamais empriunter dans le passé
on ne peut pas le faire deux fois

@moussa
Notification:
Emrunt effetué
Emprunt retourné
Retard détecté
3jrs avant l'echeance et l'echeance (00h00)

TASKS:
- [x] Inclure l envoie email dans emprunt_handler et retour_handler
- [x] Implementer le get_user_infos_with_loan_due_in_3_days(reference_date: date=today())
- [x] Un usecase: notify_user_before3days
- [x] Un usecase: notify_user_on_delay_detected
- [x] API: notify_user_before3days
- [x] API: notify_user_on_delay_detected
- [.....] Implementer le service d'envoi email (rest implent real brevo)