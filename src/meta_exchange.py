import aiohttp
import time

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

async def _request(self, method, uri, force_params=False, **kwargs):

    # set default requests timeout
    kwargs['timeout'] = 10

    # add our global requests params
    if self._requests_params:
        kwargs.update(self._requests_params)

    data = kwargs.get('data', None)
    if data and isinstance(data, dict):
        kwargs['data'] = data

        # find any requests params passed and apply them
        if 'requests_params' in kwargs['data']:
            # merge requests params into kwargs
            kwargs.update(kwargs['data']['requests_params'])
            del(kwargs['data']['requests_params'])


    # generate signature
    kwargs['data']['timestamp'] = int(time.time() * 1000)
    kwargs['data']['signature'] = self._generate_signature(kwargs['data'])

    # sort get and post params to match signature order
    if data:
        # sort post params
        kwargs['data'] = self._order_params(kwargs['data'])
        # Remove any arguments with values of None.
        null_args = [i for i, (key, value) in enumerate(kwargs['data']) if value is None]
        for i in reversed(null_args):
            del kwargs['data'][i]

    # if get request assign data array to params value for requests lib
    if data and (method == 'get' or force_params):
        kwargs['params'] = '&'.join('%s=%s' % (data[0], data[1]) for data in kwargs['data'])
        del(kwargs['data'])

    async with aiohttp.ClientSession() as session:
        async with session.getattr(self.session, method)(uri, **kwargs) as resp:

            if not str(resp.status_code).startswith('2'):
                raise Exception(resp)
            try:
                return resp.json()
            except ValueError:
                raise Exception('Invalid Response: %s' % resp.text)