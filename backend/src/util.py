import re
from retry import retry
from encrypt        import password_decrypt

def process_to_lower_with_underscore(fields):
    new_fields = {}
    for key in fields.keys():
        new_key = re.sub('([A-Z]{1})', r'_\1', key).lower()

        if isinstance(fields[key], dict):
            new_fields[new_key] = process_to_lower_with_underscore(fields[key])
            
        else:
            new_fields[new_key] = fields[key]
    
    return new_fields

def aggregate_balance(balances):
    symbols = set(b['coin_id'] for b in balances)
    out_array = []
    for symbol in symbols:
        same = list(filter(lambda x: x['coin_id'] == symbol, balances))
        out_dict = same.pop()

        out_dict['exchanges'] = [out_dict['exchange']]
        del(out_dict['exchange'])

        out_dict['total']       = float(out_dict['total'])
        out_dict['usd']         = float(out_dict['usd'])
        out_dict['available']   = float(out_dict['available'])
        for s in same:
            out_dict['total']       += float(s['total'])
            out_dict['usd']         += float(s['usd'])
            out_dict['available']   += float(s['available'])
            
            if s['exchange'] not in out_dict['exchanges']:
                out_dict['exchanges'].append(s['exchange'])

        out_array.append(out_dict)
    return out_array

def make_wallets(user, wallet_types):
    wallets = {}
    for wallet in user['wallets']:
        wallet_type = [w['name'] for w in wallet_types if w['_id'] == wallet['wallet_type']][0]
        wallets[wallet_type] = {
            'address': wallet['address'],
            'tokens': wallet['tokens']
        }
    return wallets

def make_exchanges(user, password, exchange_types):
    exchanges = {}
    for account in user['accounts']:
        exchange_name = [e['name'] for e in exchange_types if e['_id'] == account['exchange']][0]
        exchanges[exchange_name] = {
            'api_key': password_decrypt(account['api_key'].encode('utf-8'), password).decode('utf-8'),
            'api_secret': password_decrypt(account['secret'].encode('utf-8'), password).decode('utf-8')
        }
    return exchanges

@retry(5, 2)
def get_secret(secret_name):
    try:
        with open('/run/secrets/{0}'.format(secret_name), 'r') as secret_file:
            return secret_file.read()
    except IOError:
        return None