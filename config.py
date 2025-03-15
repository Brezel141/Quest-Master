class Config:
    SECRET_KEY = 'una_chiave_segreta_casuale'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    
    # Mail settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = ''  # Replace with your email
    MAIL_PASSWORD = ''     # Replace with your app password
    MAIL_DEFAULT_SENDER = 'noreply@questmaster.com'
    # Other common configurations

class DevelopmentConfig(Config):
    DEBUG = True
    # Development-specific configurations

class ProductionConfig(Config):
    DEBUG = False
    # Production-specific configurations

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False  # Disable CSRF for tests
