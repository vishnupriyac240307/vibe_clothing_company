import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'vibe_clothing_erp_default_secret_key_2026')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = True
    
    # Database URI Configuration
    # Uses DATABASE_URL if set, or defaults to SQLite DB file inside instance/data directory
    DEFAULT_DB_PATH = os.path.join(BASE_DIR, 'vibe_clothing_company.db')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{DEFAULT_DB_PATH}')
    
    # Currency Settings
    CURRENCY_SYMBOL = '₹'
    CURRENCY_CODE = 'INR'
    
    # Pagination
    ITEMS_PER_PAGE = 15
    
    # API Keys
    UNSPLASH_API_KEY = os.getenv('UNSPLASH_API_KEY', '')
    PEXELS_API_KEY = os.getenv('PEXELS_API_KEY', '')
