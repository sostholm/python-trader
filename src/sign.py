import hmac
import hashlib
from operator import itemgetter

def cdc_sign(req, api_secret):
    paramString = ""

    if "params" in req: 
        for key in req['params']:
            paramString += key
            paramString += str(req['params'][key])

    sigPayload = req['method'] + str(req['id']) + req['api_key'] + paramString + str(req['nonce'])

    return hmac.new(
        bytes(str(api_secret), 'utf-8'),
        msg=bytes(sigPayload, 'utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()

def binance_sign(data, api_secret):

    ordered_data = _order_params(data)
    query_string = '&'.join(["{}={}".format(d[0], d[1]) for d in ordered_data])
    m = hmac.new(api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
    return m.hexdigest()

def _order_params(data):
    """Convert params to list with signature as last element

    :param data:
    :return:

    """
    has_signature = False
    params = []
    for key, value in data.items():
        if key == 'signature':
            has_signature = True
        else:
            params.append((key, value))
    # sort parameters by key
    params.sort(key=itemgetter(0))
    if has_signature:
        params.append(('signature', data['signature']))
    return params