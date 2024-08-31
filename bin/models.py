from time import struct_time

from pydantic import BaseModel

class keycloak_configuration(BaseModel):
        url: str
        realm: str
        client_id: str
        client_secret: str
        auth_url: str
        token_url: str
        cert_url: str

class mango_configuration(BaseModel):
        root_user: str
        root_pass: str
        url: str