import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or' d14d42cb71e1da0efec8b229c32d7ac5db2c501ee748a672300d4c2d03d004c9'
    # Pour MySQL sans mot de passe root
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:@localhost:3306/project_salary_prediction?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }