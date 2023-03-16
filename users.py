from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from core import Firestore
from passlib.context import CryptContext
from datetime import datetime, timedelta
import json

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 4
SECRET_KEY = '123rafael'
# Context
crypt = CryptContext(schemes=["bcrypt"])

router = APIRouter(tags=['User'])
oauth2 = OAuth2PasswordBearer(tokenUrl='login')


class User(BaseModel):
    username: str
    full_name: str
    email: str
    disabled: bool = False
    admin: bool = False


class UserBD(User):
    password: str

credentials_exception_global = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # Validation
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    base = Firestore().consulta('users', 'email', '==', username)
    user = base[username]
    if user is None:
        raise credentials_exception
    return User(**user)


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

@router.post('/user')
async def users(user: UserBD):
    users_db = Firestore()
    if users_db.consulta('users', 'email', '==', user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="EL email ya existe!"
        )
    users_db.escribir(
        'users', user.email,  {'username': user.username,
                               'full_name': user.full_name,
                               'email': user.email,
                               'disabled': user.disabled,
                               'password': crypt.hash(user.password.encode('utf-8')),
                               'admin': user.admin
                               })
    user_response = users_db.consulta('users', 'email', '==', user.email)
    del user_response[user.email]['password']
    return User(**user_response[user.email])


@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    users_db = Firestore()
    user_db = users_db.consulta('users', 'email', '==', form.username)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no es correcto")
    if not crypt.verify(form.password, user_db[form.username]['password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token = create_access_token(
        data={"sub": user_db[form.username]['email']},
        expires_delta=timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.patch("/users/update/{username}")
async def update_user_me(username: str, current_user: User = Depends(get_current_active_user)):
    Firestore().update_field_doc('users', current_user.email, {'username' : username})
    user = Firestore().consulta('users', 'email', '==', current_user.email)
    del user[current_user.email]['password']
    return User(**user[current_user.email])

@router.delete("/users/delete")
async def delete_user_me(current_user: User = Depends(get_current_active_user)):
    print(current_user.email)
    Firestore().deleteDocument('users', current_user.email)
    return {'delete' : current_user.email}

@router.get("/users/all")
async def get_all_users(current_user: User = Depends(get_current_active_user)):
    if not current_user.admin:
        raise credentials_exception_global
    users = Firestore().leer('users')
    return json.dumps(users)




