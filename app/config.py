import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Salesforce
    SF_USERNAME = os.getenv("SF_USERNAME")
    SF_PASSWORD = os.getenv("SF_PASSWORD")
    SF_SECURITY_TOKEN = os.getenv("SF_SECURITY_TOKEN")
    SF_DOMAIN = os.getenv("SF_DOMAIN", "login")

    # Postgres
    PG_HOST = os.getenv("PG_HOST", "127.0.0.1")
    PG_PORT = int(os.getenv("PG_PORT", "5432"))
    PG_DB   = os.getenv("PG_DB", "pima")
    PG_USER = os.getenv("PG_USER", "postgres")
    PG_PASSWORD = os.getenv("PG_PASSWORD", "postgres")

    # Audit
    MIGRATION_OPERATOR_EMAIL = os.getenv("MIGRATION_OPERATOR_EMAIL", "ops@pima.local")
    SYSTEM_USER_ID = os.getenv("SYSTEM_USER_ID", "00000000-0000-0000-0000-000000000001")

    @property
    def pg_url(self) -> str:
        return f"postgresql+psycopg2://{self.PG_USER}:{self.PG_PASSWORD}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DB}"

settings = Settings()
