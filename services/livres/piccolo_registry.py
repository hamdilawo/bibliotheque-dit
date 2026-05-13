# Séparé de piccolo_conf.py pour éviter l'import circulaire
# piccolo_conf.py  ← utilisé par tables.py (via core/database.py)
# piccolo_registry.py ← utilisé uniquement par le CLI Piccolo
from piccolo.conf.apps import AppRegistry
from piccolo_conf import DB  # noqa: F401  (réexposé pour que le CLI trouve DB)

APP_REGISTRY = AppRegistry(apps=["features.books.piccolo_app"])