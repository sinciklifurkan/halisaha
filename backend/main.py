from datetime import datetime, timedelta, timezone
import jwt
import os

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pwdlib import PasswordHash
from dotenv import load_dotenv

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

security = HTTPBearer()

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 900


password_hash = PasswordHash.recommended()

users = {}


class SignupRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


def create_access_token(username: str):
    expire = datetime.now(timezone.utc) + timedelta(
        seconds=ACCESS_TOKEN_EXPIRE_SECONDS
    )

    payload = {
        "sub": username,
        "exp": expire
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Gecersiz token"
            )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token suresi dolmus"
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Gecersiz token"
        )

    user = users.get(username)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Kullanici bulunamadi"
        )

    return user


@app.get("/")
def home():
    return {
        "message": "Backend calisiyor"
    }


@app.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(data: SignupRequest):

    if data.username in users:
        raise HTTPException(
            status_code=409,
            detail="Bu kullanici zaten kayitli"
        )

    hashed_password = password_hash.hash(
        data.password
    )

    users[data.username] = {
        "username": data.username,
        "hashed_password": hashed_password
    }

    return {
        "message": "Kullanici olusturuldu",
        "username": data.username
    }


@app.get("/users")
def get_users():
    return [
        {
            "username": username
        }
        for username in users
    ]


@app.post("/login")
def login(data: LoginRequest):

    user = users.get(data.username)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Kullanici adi veya sifre hatali"
        )

    password_is_correct = password_hash.verify(
        data.password,
        user["hashed_password"]
    )

    if not password_is_correct:
        raise HTTPException(
            status_code=401,
            detail="Kullanici adi veya sifre hatali"
        )

    access_token = create_access_token(
        data.username
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return {
        "username": current_user["username"]
    }