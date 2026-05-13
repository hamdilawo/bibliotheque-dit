import os

ARTIFACTS_PATH = os.environ.get('ARTIFACTS_PATH', '/app/model/recommender_artifacts.pkl')
DATA_PATH = os.environ.get('DATA_PATH', '/app/data/emprunt.csv')
BOOKS_PATH = os.environ.get('BOOKS_PATH', '/app/data/books.json')

SERVICE_LIVRES_URL = os.environ.get('SERVICE_LIVRES_URL', 'http://livres:8001')
SERVICE_EMPRUNTS_URL = os.environ.get('SERVICE_EMPRUNTS_URL', 'http://emprunts:8003')

N_RECOMMENDATIONS = int(os.environ.get('N_RECOMMENDATIONS', '5'))
ALPHA = float(os.environ.get('ALPHA', '0.6'))
MIN_USER_RATINGS = int(os.environ.get('MIN_USER_RATINGS', '3'))
REF_WEIGHT = float(os.environ.get('REF_WEIGHT', '0.3'))
