"""
Configuration Piccolo ORM pour le service Livres.
Piccolo utilise ce fichier pour les migrations (piccolo migrations new/run).
"""
from piccolo.conf.apps import AppConfig
from features.books.tables import Livre, Categorie

APP_CONFIG = AppConfig(
    app_name="books",
    migrations_folder_path="features/books/migrations",
    table_classes=[Categorie, Livre],
    migration_dependencies=[],
    commands=[],
)