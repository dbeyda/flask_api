import sqlite3 as sql
import jwt
from datetime import datetime, timedelta
from passlib.hash import sha256_crypt
from flask import abort
import app.config as config


secret = config.SECRET_KEY
token_minutes = config.TOKEN_MINUTES

def generate_auth_token(user):
	payload = {
            'exp': datetime.utcnow() + timedelta(minutes=token_minutes),
            'iat': datetime.utcnow(),
            'user': user
        }
	token = jwt.encode(payload, secret, algorithm = 'HS256')
	return token

def register_user(user, password):
	hashed_pass = hash_password(password)
	con = sql.connect("app/database.db")
	cursor = con.cursor()
	checagem = cursor.execute("SELECT User FROM tokens WHERE IsActive = 1 AND User = ?", (user, )).fetchall()
	if len(checagem) > 0:
		abort(400)
	cursor.execute("INSERT INTO tokens (User, Hash, IsActive) VALUES (?, ?, ?)",
		(user, hashed_pass, 1))
	con.commit()
	con.close()
	return True
def get_user_hash(user):
	con = sql.connect("app/database.db")
	cursor = con.cursor()
	user_hash = cursor.execute("SELECT Hash FROM tokens WHERE IsActive = 1 AND User = ?", (user,)).fetchall()
	con.commit()
	con.close()
	return user_hash
def delete_user(user):
	con = sql.connect("app/database.db")
	cursor = con.cursor()
	cursor.execute("UPDATE tokens SET IsActive = 0 WHERE User = ? AND IsActive = 1", (user,))
	con.commit()
	con.close()
	return True

def hash_password(password):
	return sha256_crypt.hash(password)
def verify_password(password, hash):
	return sha256_crypt.verify(password, hash)
