from datetime import timedelta
import os

databaseUrl = os.environ["DATABASE_URL"]

class Configuration:
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes = 60)
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:123@{databaseUrl}/authorization"