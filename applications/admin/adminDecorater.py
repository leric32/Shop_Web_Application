from functools import wraps
from flask import Response
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask import jsonify

def increment(value):
    def inner_increment(function):
        @wraps(function)
        def decorator(*arguments, **keyword_arguments):
            result = function(*arguments, **keyword_arguments)
            return result + value

        return decorator

    return inner_increment


def double(function):
    def decorator(*arguments, **keyword_arguments):
        result = function(*arguments, **keyword_arguments)
        return result * 2

    return decorator


@double
@increment(value=10)
def add(a, b):
    return a + b


# print(add(1, 2))

def role_check(role):
    def inner_role(function):
        @wraps(function)
        def decorator(*arguments, **keyword_arguments):
            verify_jwt_in_request()
            claims = get_jwt()
            if ("roles" in claims) and (role in claims["roles"]):
                return function(*arguments, **keyword_arguments)
            else:
                return jsonify(msg='Missing Authorization Header'), 401
        return decorator
    return inner_role
