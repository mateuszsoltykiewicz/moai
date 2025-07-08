# /Python/libraries/core/async_security/__init__.py
import jwt

def encode_jwt(payload, secret, algorithm='HS256'):
    return jwt.encode(payload, secret, algorithm=algorithm)

def decode_jwt(token, secret, algorithms=['HS256']):
    return jwt.decode(token, secret, algorithms=algorithms)
