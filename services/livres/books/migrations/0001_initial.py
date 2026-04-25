from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Categorie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
            ],
            options={'verbose_name': 'Catégorie', 'ordering': ['nom']},
        ),
        migrations.CreateModel(
            name='Livre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titre', models.CharField(max_length=255)),
                ('auteur', models.CharField(max_length=255)),
                ('isbn', models.CharField(max_length=13, unique=True)),
                ('editeur', models.CharField(blank=True, max_length=255)),
                ('annee_publication', models.PositiveIntegerField(blank=True, null=True)),
                ('langue', models.CharField(choices=[('fr', 'Français'), ('en', 'Anglais'), ('ar', 'Arabe'), ('es', 'Espagnol')], default='fr', max_length=2)),
                ('description', models.TextField(blank=True)),
                ('nombre_pages', models.PositiveIntegerField(blank=True, null=True)),
                ('quantite_totale', models.PositiveIntegerField(default=1)),
                ('quantite_disponible', models.PositiveIntegerField(default=1)),
                ('date_ajout', models.DateTimeField(auto_now_add=True)),
                ('date_modification', models.DateTimeField(auto_now=True)),
                ('couverture_url', models.URLField(blank=True)),
                ('actif', models.BooleanField(default=True)),
                ('categorie', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='livres', to='books.categorie')),
            ],
            options={'ordering': ['titre']},
        ),
        migrations.AddIndex(
            model_name='livre',
            index=models.Index(fields=['isbn'], name='books_livre_isbn_idx'),
        ),
        migrations.AddIndex(
            model_name='livre',
            index=models.Index(fields=['auteur'], name='books_livre_auteur_idx'),
        ),
        migrations.AddIndex(
            model_name='livre',
            index=models.Index(fields=['titre'], name='books_livre_titre_idx'),
        ),
    ]
