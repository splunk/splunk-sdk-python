import logging
import traceback
import json

from functools import wraps

def json_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        decorated = json_exception_handler(json_payload_extractor(func))
        return decorated(*args, **kwargs)
    return wrapper


def json_payload_extractor(func):
    @wraps(func)
    def wrapper(self, in_string):
        try:
            request = json.loads(in_string)
            kwargs = {'request': request, 'in_string': in_string}
            if 'payload' in request:
                # if request contains payload, parse it and add it as payload parameter
                kwargs['payload'] = json.loads(request['payload'])
            if 'query' in request:
                # if request contains query, parse it and add it as query parameter
                kwargs['query'] = _convert_tuples_to_dict(request['query'])
            return func(self, **kwargs)
        except ValueError as e:
            return {'payload': {'success': 'false', 'result': f'Error parsing JSON: {e}'},
                    'status': 400
                    }
    return wrapper


def json_exception_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(
                f'error={repr(e)} traceback={traceback.format_exc()}')
            return {'payload': {'success': 'false', 'message': f'Error: {repr(e)}'},
                    'status': 500
                    }
    return wrapper


def _convert_tuples_to_dict(tuples):
    return {t[0]: t[1] for t in tuples}

