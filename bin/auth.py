import jwt
import logging
from jwt import PyJWKClient
from typing import Annotated
from config import keycloak_conf
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi import Security, HTTPException, status, Depends

logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG)

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=keycloak_conf.auth_url,
    tokenUrl=keycloak_conf.token_url,
)

# Token from keycloak
async def authenticate(token: str = Security(oauth2_scheme)) -> dict:
    try:
        jwks_client = PyJWKClient(keycloak_conf.cert_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=keycloak_conf.client_id,
            options={"verify_exp": True},
        )
    except Exception as e:
        logger.info(f"error -- {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="failed to authenticate : " + str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


def has_role(role_name: str):
    async def check_role(
            token_data: Annotated[dict, Depends(authenticate)]
    ):
        logger.debug(token_data)
        # logger.debug(token_data["resource_access"][keycloak_conf.client_id]["roles"])
        # logger.debug(role_name in token_data["resource_access"][keycloak_conf.client_id]["roles"])
        try:
            if role_name not in token_data['resource_access'][keycloak_conf.client_id]['roles']:
                raise HTTPException(status_code=403, detail=f"Unauthorized access. Does not have role='{role_name}")
        except Exception as e:
            raise HTTPException(status_code=403, detail=f"Unauthorized access. Does not have role='{role_name}. {e}")
        return(token_data)

    return check_role