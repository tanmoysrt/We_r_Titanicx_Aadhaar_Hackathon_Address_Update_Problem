from hackathon_adhaar_solution.settings import SECRET_KEY
import datetime
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError


def encode(txnid, is_landlord=0):
    header = {'alg': 'HS256', "typ": "jwt"}
    payload = {'_txnid': str(txnid), '_landlord' : is_landlord, "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30)}
    jwtt = jwt.encode(payload, SECRET_KEY, algorithm="HS256", headers=header)
    return jwtt


def decode(data):
    try:
        jwt_payload = jwt.decode(data, SECRET_KEY, algorithms=["HS256"])
        return True, jwt_payload["_txnid"], jwt_payload["_landlord"]
    except ExpiredSignatureError:
        return False, "expired"
    except InvalidSignatureError:
        return False, "invalid"
    except:
        return False, "unknown"
