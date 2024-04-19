# modules/auth/oauth.py
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import decode, PyJWTError
from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

# Simulación de usuarios (reemplazar con tu propio sistema de autenticación)
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$7AYkW8.OkrRkSgIFalvTNO9WqUvAE8bb1zMXtUlywBvsJEpR7cazi",  # Password: secret
        "disabled": False,
        "role": "user"
    }
}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception

    user = fake_users_db.get(username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    if current_user["disabled"]:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def check_permissions(required_role: Optional[str] = None, current_user: dict = Depends(get_current_active_user)):
    if required_role and current_user.get("role") != required_role:
        raise HTTPException(status_code=403, detail="Not enough permissions")