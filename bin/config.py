from models import keycloak_configuration, mango_configuration

keycloak_conf = keycloak_configuration(
    url="http://127.0.0.1:8085/",
    realm="small_bank",
    client_id="sm:api",
    client_secret="xDRrKj5HfffF2BEmqyi2FyP5bWdIRnZQ", # get this value from keycloak -> realm=small_bank -> client=sm:api -> client secrets
    auth_url="http://127.0.0.1:8085/realms/small_bank/protocol/openid-connect/auth",
    token_url="http://127.0.0.1:8085/realms/small_bank/protocol/openid-connect/token",
    cert_url = "http://127.0.0.1:8085/realms/small_bank/protocol/openid-connect/certs",
)

mango_conf = mango_configuration(
    root_user="admin", # get this value from file=docker_compose_env
    root_pass="admin", # get this value from file=docker_compose_env
    url = "localhost:27017",
)