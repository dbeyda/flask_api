import sqlite3 as sql
import jwt
from datetime import datetime, timedelta

secret = "\xba\x88\xc0/\xbf\xf1\xe6I\x98r\xee\x0f\xe8p\x97\xb3^z\xec\xfa\x06b\x8f\x19c+A&\x91N30;\xba\xac\
xe3\xa9\x11mA\x90\x13\x98\x12}/&\x85:uG8"
token_valid_seconds = 40

users = {
	'joao':[0, 'aha'],
	'maria':[1, 'aba'],
	'rafa':[2, 'port']
}


def generate_auth_token(user):
	payload = {
            'exp': datetime.utcnow() + timedelta(days=0, seconds=token_valid_seconds),
            'iat': datetime.utcnow(),
            'user': user
        }
	token = jwt.encode(payload, secret, algorithm = 'HS256')
	return token


