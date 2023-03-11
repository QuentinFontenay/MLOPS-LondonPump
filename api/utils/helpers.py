import os
from dotenv import load_dotenv

load_dotenv()

def path_file():
    if os.getenv('PYTHON_ENV') == 'development' or os.getenv('PYTHON_ENV') == 'testing':
        return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'public')
    else:
        return os.path.abspath('../../data/modele')
