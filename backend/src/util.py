import re

def process_to_lower_with_underscore(fields):
    new_fields = {}
    for key in fields.keys():
        new_key = re.sub('([A-Z]{1})', r'_\1', key).lower()

        if isinstance(fields[key], dict):
            new_fields[new_key] = process_to_lower_with_underscore(fields[key])
            
        else:
            new_fields[new_key] = fields[key]
    
    return new_fields