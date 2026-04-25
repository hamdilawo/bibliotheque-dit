from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Utilisateur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('nom', models.CharField(max_length=100)),
                ('prenom', models.CharField(max_length=100)),
                ('numero_carte', models.CharField(max_length=20, unique=True)),
                ('type_utilisateur', models.CharField(
                    choices=[('ETUDIANT', 'Étudiant'), ('PROFESSEUR', 'Professeur'),
                             ('PERSONNEL', 'Personnel'), ('ADMIN', 'Administrateur')],
                    default='ETUDIANT', max_length=20
                )),
                ('statut', models.CharField(
                    choices=[('ACTIF', 'Actif'), ('SUSPENDU', 'Suspendu'), ('INACTIF', 'Inactif')],
                    default='ACTIF', max_length=20
                )),
                ('telephone', models.CharField(blank=True, max_length=20)),
                ('adresse', models.TextField(blank=True)),
                ('date_naissance', models.DateField(blank=True, null=True)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='photos/')),
                ('quota_emprunts', models.PositiveIntegerField(default=3)),
                ('emprunts_en_cours', models.PositiveIntegerField(default=0)),
                ('date_inscription', models.DateTimeField(auto_now_add=True)),
                ('date_modification', models.DateTimeField(auto_now=True)),
                ('derniere_connexion_api', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
            ],
            options={'ordering': ['nom', 'prenom']},
        ),
        migrations.AddIndex(
            model_name='utilisateur',
            index=models.Index(fields=['email'], name='users_email_idx'),
        ),
        migrations.AddIndex(
            model_name='utilisateur',
            index=models.Index(fields=['numero_carte'], name='users_carte_idx'),
        ),
        migrations.AddIndex(
            model_name='utilisateur',
            index=models.Index(fields=['type_utilisateur'], name='users_type_idx'),
        ),
    ]
