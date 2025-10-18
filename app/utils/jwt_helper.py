import jwt
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta, timezone      # Import timezone
from typing import Dict, Any

load_dotenv() # Load environment variables from .env file

SECRET_KEY = os.getenv("SECRET_KEY")

ALGORITHM: str = "HS256"

# 1: Cast environment variables to int() here. 
# They are strings when retrieved from os.getenv(), which causes the TypeError in timedelta.
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))


def create_access_token(data: Dict):
    payload: Dict = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expire.timestamp(), "type": "access"})
    encoden_jwt = jwt.encode(payload, SECRET_KEY, ALGORITHM)
    return encoden_jwt

def create_refresh_token(data: Dict):
    payload: Dict = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload.update({"exp": expire.timestamp(), "type": "refresh"})
    encoden_jwt = jwt.encode(payload, SECRET_KEY, ALGORITHM)
    return encoden_jwt


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    
        



