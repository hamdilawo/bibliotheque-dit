from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Emprunt',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False)),
                ('utilisateur_id', models.PositiveIntegerField(db_index=True)),
                ('livre_id', models.PositiveIntegerField(db_index=True)),
                ('utilisateur_nom', models.CharField(blank=True, max_length=200)),
                ('utilisateur_carte', models.CharField(blank=True, max_length=20)),
                ('livre_titre', models.CharField(blank=True, max_length=255)),
                ('livre_isbn', models.CharField(blank=True, max_length=13)),
                ('livre_auteur', models.CharField(blank=True, max_length=255)),
                ('date_emprunt', models.DateTimeField(auto_now_add=True)),
                ('date_retour_prevue', models.DateField()),
                ('date_retour_effective', models.DateField(blank=True, null=True)),
                ('statut', models.CharField(
                    choices=[
                        ('EN_COURS', 'En cours'), ('RETOURNE', 'Retourné'),
                        ('EN_RETARD', 'En retard'), ('PERDU', 'Perdu'),
                    ],
                    default='EN_COURS', max_length=20
                )),
                ('jours_retard', models.PositiveIntegerField(default=0)),
                ('penalite_fcfa', models.DecimalField(
                    decimal_places=2, default=0, max_digits=10)),
                ('notes', models.TextField(blank=True)),
            ],
            options={'ordering': ['-date_emprunt']},
        ),
        migrations.AddIndex(
            model_name='emprunt',
            index=models.Index(
                fields=['utilisateur_id', 'statut'], name='loans_user_statut_idx'),
        ),
        migrations.AddIndex(
            model_name='emprunt',
            index=models.Index(
                fields=['livre_id', 'statut'], name='loans_livre_statut_idx'),
        ),
        migrations.AddIndex(
            model_name='emprunt',
            index=models.Index(
                fields=['date_retour_prevue'], name='loans_retour_date_idx'),
        ),
    ]
