from piccolo.apps.migrations.auto.migration_manager import MigrationManager

ID = "2026-05-04T00:00:00"
VERSION = "1.16.0"
DESCRIPTION = "Initial migration - Categorie and Livre tables"


async def forwards():
    manager = MigrationManager(
        migration_id=ID,
        app_name="books",
        description=DESCRIPTION,
    )

    manager.add_table(
        class_name="Categorie",
        tablename="categorie",
    )
    manager.add_column(
        table_class_name="Categorie",
        tablename="categorie",
        column_name="nom",
        db_column_name="nom",
        column_class_name="Varchar",
        column_class=Varchar,
        params={"length": 100, "unique": True, "null": False, "primary_key": False, "required": False},
    )
    manager.add_column(
        table_class_name="Categorie",
        tablename="categorie",
        column_name="description",
        db_column_name="description",
        column_class_name="Text",
        column_class="Text",
        params={"default": "", "null": False, "primary_key": False, "required": False},
    )

    manager.add_table(
        class_name="Livre",
        tablename="livres",
    )

    return manager