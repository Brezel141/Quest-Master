from app import create_app
from config import DevelopmentConfig, ProductionConfig
import os

# Use ProductionConfig in production, DevelopmentConfig in development
config = ProductionConfig if os.environ.get('FLASK_ENV') == 'production' else DevelopmentConfig
app = create_app(config)

if __name__ == '__main__':
    app.run()
