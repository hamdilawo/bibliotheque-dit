from decouple import config

MODEL_PATH = config('MODEL_PATH', default='/app/model/model.pkl')
DATA_PATH = config('DATA_PATH', default='/app/data/loans.csv')
SERVICE_LIVRES_URL = config('SERVICE_LIVRES_URL', default='http://livres:8001')
SERVICE_EMPRUNTS_URL = config('SERVICE_EMPRUNTS_URL', default='http://emprunts:8003')
N_RECOMMENDATIONS = config('N_RECOMMENDATIONS', default=5, cast=int)
