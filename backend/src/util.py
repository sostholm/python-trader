import re
from retry import retry

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

@retry(5, 2)
def get_secret(secret_name):
    try:
        with open('/run/secrets/{0}'.format(secret_name), 'r') as secret_file:
            return secret_file.read()
    except IOError:
        return None