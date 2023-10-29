import os

databaseUrl = os.environ["DATABASE_URL"]

class Configuration:
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:123@{databaseUrl}/store"
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    # So that we perserve the order of dict items in response
    JSON_SORT_KEYS = False