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

@retry(5, 2)
def get_secret(secret_name):
    try:
        with open('/run/secrets/{0}'.format(secret_name), 'r') as secret_file:
            return secret_file.read()
    except IOError:
        return None