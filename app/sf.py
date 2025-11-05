from simple_salesforce import Salesforce
from .config import settings

def sf_client() -> Salesforce:
    return Salesforce(
        username=settings.SF_USERNAME,
        password=settings.SF_PASSWORD,
        security_token=settings.SF_SECURITY_TOKEN,
        domain=settings.SF_DOMAIN,
    )

def query_all(sf: Salesforce, soql: str):
    res = sf.query_all(soql)
    for r in res.get("records", []):
        r.pop("attributes", None)
        yield r
