import uvicorn
import logging
import mango
from auth import has_role
from urllib.parse import parse_qs
from fastapi import FastAPI, Depends, Request, HTTPException

logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG)
# logger.info("i am launching")
# logger.debug("am i in debug mode?")

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello ..... Welcome to Small Bank"}

@app.get("/bank_user/{bank}")
def get_account(bank: str, token = Depends(has_role("account_owner"))):
    """
    ### Test 1 -- Authenticate as bob(or charlie) and check balance
    * GET    /bank_user/{bank}     # for bob use bank=icici, for charlie use bank=hdfc

    ### Test 2 -- Authenticate as bob(or charlie) and perform credit/debit operation
    * PUT    /bank_user/{bank}     # for bob use bank=icici, for charlie use bank=hdfc
    """
    user = token['preferred_username']
    if f"/{bank}" not in token['groups']:
        raise HTTPException(status_code=403, detail=f"Unauthorized access. user {user} does not belong to {bank} bank")
    # logger.info(f"hello {user}")
    # logger.info(f"you have roles {token['resource_access'][keycloak_conf.client_id]['roles']} in group {token['groups']}")
    balance = str(mango.balance(bank, user))
    logger.info(f"balance money {balance}")
    return {"message": f"balance money is {balance}"}


@app.put("/bank_user/{bank}")
async def put_account(bank: str, amount: int, token = Depends(has_role("account_owner"))):
    """
    ### Test 1 -- Authenticate as bob(or charlie) and check balance
    * GET    /bank_user/{bank}     # for bob use bank=icici, for charlie use bank=hdfc

    ### Test 2 -- Authenticate as bob(or charlie) and perform credit/debit operation
    * PUT    /bank_user/{bank}     # for bob use bank=icici, for charlie use bank=hdfc
    """
    user = token['preferred_username']
    if amount == 0:
        raise HTTPException(status_code=400, detail=f"Amount should not be zero")
    result = mango.debit_credit(bank, user, amount)
    logger.debug(result)
    balance = str(mango.balance(bank, user))
    return {"message": f"new balance is {balance}"}

@app.get("/bank_teller/{bank}/{user}")
def get_all_account(bank: str, user: str|None, token = Depends(has_role("bank_teller")) ):
    login = token['preferred_username']
    if f"/{bank}" not in token['groups']:
        raise HTTPException(status_code=403, detail=f"Unauthorized access. bank teller {login} does not belong to {bank} bank")
    obj = mango.all_user_balance(bank, user)
    logger.info(obj)
    return {"message": "get all account"}

@app.put("/bank_teller/{bank}/{user}")
async def create_account(bank: str, user: str, token = Depends(has_role("bank_teller"))):
    """
    ### First API call
    * Before users can use their account, bank teller needs to create account for bob and charlie
    * Go to http://127.0.0.1:8086/docs
      * Authenticate as icici_teller
      * Extend PUT /bank_teller/{bank}/{user}
      * Try, giving bank=icici, user=bob
    * Now logout, restart browser or clear session for icici_teller from keycloak admin page
      * And, Authenticate as hdfc_teller
      * Extend PUT /bank_teller/{bank}/{user}
      * Try, giving bank=hdfc, user=charlie

    ### Note (warning|caution):
      * In keycloak, bob belongs to group=icici and charlie belongs to group=hdfc
      * hence, we choose icici_teller to create bobs account
      * and, hdfc_teller to create charlie account
      * incase, icici_teller also creates account for charlie -- then charlie will have two accounts in both the banks
        * But, to use icici account, charlie will need to be also added in keycloak group=icici
    """
    login = token['preferred_username']
    if f"/{bank}" not in token['groups']:
        raise HTTPException(status_code=403, detail=f"Unauthorized access. bank teller {login} does not belong to {bank} bank")
    mango.create_account(bank, user)
    return {"message": "account created."}

if __name__ == '__main__':
    uvicorn.run('main:app', host="127.0.0.1", port=8086)