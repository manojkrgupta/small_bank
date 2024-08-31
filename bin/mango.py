import logging
import pymongo as mg
from fastapi import HTTPException
from config import mango_conf

logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG)
mgh = mg.MongoClient(f"mongodb://{mango_conf.root_user}:{mango_conf.root_pass}@{mango_conf.url}/")
mdb = mgh["small_banks"]

# -------------------------------------
# Initialise in Mongo DB
# -------------------------------------
# yahoo_mango_db> db.createCollection('banks.icici')
# { ok: 1 }
# yahoo_mango_db> db.createCollection('banks.hdfc')
# { ok: 1 }
# yahoo_mango_db> db.banks.icici.ensureIndex({'user': 1}, {unique: true})
# [ 'user_1' ]
# yahoo_mango_db> db.banks.hdfc.ensureIndex({'user': 1}, {unique: true})
# [ 'user_1' ]

# Atomic operation in Mongodb
# --------------------------------
# Credit Example 1
# db.banks.HDFC.updateOne({'user': 'bob', amount: {$gt : -1}}, {$inc: { amount: 100}, $push: { auditlog: {val: 100, date: new Date() }}})
# Credit Example 2
# db.banks.HDFC.updateOne({'user': 'bob'}, {$inc: { amount: 100}, $push: { auditlog: {val: 100, date: new Date() }}})
#
# Debit -->
# db.banks.HDFC.updateOne({'user': 'bob', amount: {$gte : 10}}, {$inc: { amount: -10}, $push: { auditlog: {val: -10, date: new Date() }}})

# --------------------------------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------------------------------
def debit_credit(bank, user, amount):
    if amount == 0:
        raise HTTPException(status_code=400, detail=f"Amount should not be zero")

    if amount > 0: # credit
        m_filter = {'user': user}
    else: # debit
        m_filter = {'user': user, 'amount': {'$gte' : -1*amount}}

    result = mdb.banks[bank].bulk_write([mg.UpdateOne(
        m_filter,
        {'$inc': { 'amount': amount}, '$push': { 'auditlog': {'val': amount, 'date': 'new Date()' }}}
    )])

    if result.modified_count < 1:
        raise HTTPException(status_code=403, detail=f"Unauthorized access. either user {user} not found in bank={bank}. or not sufficient fund.")
    return result

# --------------------------------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------------------------------
def balance(bank, user):
    obj = mdb["banks"][bank].find_one({'user': user})
    logger.debug(obj)
    if obj: return(obj['amount'])
    else: raise HTTPException(status_code=403, detail=f"Unauthorized access. user {user} not found in bank={bank}")

# --------------------------------------------------------------------------------------------------------
#
# --------------------------------------------------------------------------------------------------------
def all_user_balance(bank, user=None):
    if user is not None:
        obj = mdb["banks"][bank].find_one({'user': user})
        logger.debug(obj)
        if obj: return([{user: obj['amount']}]) # list of dict
        else: raise HTTPException(status_code=403, detail=f"Unauthorized access. user {user} not found in bank={bank}")
    obj = []
    for r in mdb["banks"][bank].find({}):
        obj.append({r['user']: r['amount']}) # list of dict
    return(obj)

# --------------------------------------------------------------------------------------------------------
#
# This will be only done by bank teller (example teller_hdfc, or teller_icici)
# --------------------------------------------------------------------------------------------------------
def create_account(bank, user, attributes=dict()):
    try:
        del attributes['user']
        del attributes['amount']
    except KeyError: pass

    m_obj = f"banks.{bank}" # collection
    try:
        mdb.validate_collection(m_obj) # We need to check if bank exist, else mongo db will create by default -- which is bad.
        mdb["banks"][bank].bulk_write([mg.InsertOne({'user': user, 'amount': 0, **attributes})])
    except mg.errors.OperationFailure as e:
        logger.error(f"failed to create account={user} in bank={bank}. Exception = {e}")
        raise HTTPException(status_code=403, detail=f"failed to create account={user} in bank={bank}. Exception = {e}")
