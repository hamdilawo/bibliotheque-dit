

from django.db import models


class RetourEmprunt(models.Model):
    id = models.UUIDField(primary_key=True)

    # Others fields

    class Meta:
        app_label = "loans"
