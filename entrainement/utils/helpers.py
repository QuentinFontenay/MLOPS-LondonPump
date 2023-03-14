import os
from dotenv import load_dotenv

load_dotenv()

def path_file():
    if os.getenv('PYTHON_ENV') == 'development':
        return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    else:
        return os.path.abspath('../../data/modele')
